import test from "node:test";
import assert from "node:assert/strict";
import { createHttpClient, queryString } from "../src/services/httpClient.js";
const response = (body, status = 200) =>
  new Response(body === null ? null : JSON.stringify(body), { status });

test("bearer token stays in memory; requests include cookies and exact decimal strings", async () => {
  const calls = [];
  const client = createHttpClient({
    fetchImpl: async (url, options) => {
      calls.push([url, options]);
      return response(
        url.endsWith("/login")
          ? { access_token: "private-token", user: { id: "u1" } }
          : { amount: "123456.7800" },
      );
    },
  });
  await client.authenticate("/auth/login", {
    email: "a@example.test",
    password: "pass",
  });
  const result = await client.request("/transactions", {
    method: "POST",
    body: { amount: "123456.7800" },
  });
  assert.equal(calls[1][1].headers.Authorization, "Bearer private-token");
  assert.equal(calls[1][1].credentials, "include");
  assert.equal(JSON.parse(calls[1][1].body).amount, "123456.7800");
  assert.equal(result.amount, "123456.7800");
  assert.equal(client.accessToken, undefined);
});

test("concurrent unauthorized requests share one refresh and retry with new token", async () => {
  let refreshes = 0;
  const client = createHttpClient({
    fetchImpl: async (url, options) => {
      if (url.endsWith("/refresh")) {
        refreshes++;
        await new Promise((resolve) => setTimeout(resolve, 10));
        return response({ access_token: "rotated", user: { id: "u1" } });
      }
      return options.headers.Authorization === "Bearer rotated"
        ? response({ ok: true })
        : response({ detail: "Expired" }, 401);
    },
  });
  assert.deepEqual(
    await Promise.all([
      client.request("/dashboard"),
      client.request("/accounts"),
      client.refresh(),
    ]),
    [{ ok: true }, { ok: true }, { id: "u1" }],
  );
  assert.equal(refreshes, 1);
});

test("late 401 reuses already rotated token without another refresh", async () => {
  let refreshes = 0;
  const client = createHttpClient({
    fetchImpl: async (url, options) => {
      if (url.endsWith("/refresh")) {
        refreshes++;
        return response({ access_token: "new", user: { id: "u1" } });
      }
      if (!options.headers.Authorization && url.endsWith("/slow"))
        await new Promise((resolve) => setTimeout(resolve, 25));
      return options.headers.Authorization
        ? response({ ok: true })
        : response({}, 401);
    },
  });
  await Promise.all([client.request("/fast"), client.request("/slow")]);
  assert.equal(refreshes, 1);
});

test("failed refresh ends session and does not loop or replay mutation", async () => {
  const calls = [],
    sessions = [];
  const client = createHttpClient({
    onSession: (user) => sessions.push(user),
    fetchImpl: async (url) => {
      calls.push(url);
      return response({ detail: "Sign in again." }, 401);
    },
  });
  await assert.rejects(
    client.request("/accounts", { method: "POST", body: { balance: "10.00" } }),
    { status: 401 },
  );
  assert.deepEqual(calls, ["/api/v1/accounts", "/api/v1/auth/refresh"]);
  assert.deepEqual(sessions, [null]);
});

test("public login failure never refreshes and safe errors hide server internals", async () => {
  const calls = [];
  const client = createHttpClient({
    fetchImpl: async (url) => {
      calls.push(url);
      return response({ detail: "wrong password" }, 401);
    },
  });
  await assert.rejects(client.authenticate("/auth/login", {}), {
    message: "wrong password",
  });
  assert.equal(calls.length, 1);
  const broken = createHttpClient({
    fetchImpl: async () =>
      response({ detail: "secret database internals" }, 500),
  });
  await assert.rejects(broken.request("/dashboard"), {
    message: "Barakah is temporarily unavailable. Please try again.",
  });
});

test("logout waits for rotation and only clears session after cookie revocation", async () => {
  const calls = [],
    sessions = [];
  const client = createHttpClient({
    onSession: (user) => sessions.push(user),
    fetchImpl: async (url, options) => {
      calls.push([url, options.headers.Authorization]);
      if (url.endsWith("/refresh")) {
        await new Promise((resolve) => setTimeout(resolve, 10));
        return response({ access_token: "new", user: { id: "u1" } });
      }
      return response(null, 204);
    },
  });
  await Promise.all([client.refresh(), client.logout()]);
  assert.deepEqual(calls, [
    ["/api/v1/auth/refresh", undefined],
    ["/api/v1/auth/logout", "Bearer new"],
  ]);
  assert.equal(sessions.at(-1), null);
});

test("demo reset refreshes an expired access token before replacing the session", async () => {
  const calls = [], sessions = [];
  const client = createHttpClient({
    onSession: user => sessions.push(user),
    fetchImpl: async (url, options) => {
      calls.push(url);
      if (url.endsWith("/refresh")) return response({ access_token: "rotated", user: { id: "old-demo" } });
      if (options.headers.Authorization !== "Bearer rotated") return response({ error: { code: "unauthorized" } }, 401);
      return response({ access_token: "new-demo-token", user: { id: "new-demo" } });
    },
  });
  await client.replaceSession("/auth/demo/reset");
  assert.deepEqual(calls, ["/api/v1/auth/demo/reset", "/api/v1/auth/refresh", "/api/v1/auth/demo/reset"]);
  assert.equal(sessions.at(-1).id, "new-demo");
});

test("HTML API fallback fails clearly instead of accepting a null session", async () => {
  const client = createHttpClient({ fetchImpl: async () => new Response("<html>Static frontend</html>", { status: 200 }) });
  await assert.rejects(client.authenticate("/auth/register", {}), { code: "api_not_connected" });
});

test("query parameters encode filters, omit blanks and preserve false/zero", () => {
  assert.equal(
    queryString({
      q: "food & drink",
      empty: "",
      none: null,
      archived: false,
      offset: 0,
    }),
    "?q=food+%26+drink&archived=false&offset=0",
  );
});

test("mutation CSRF header comes from current readable cookie and error envelope is shown", async () => {
  let options;
  const client = createHttpClient({
    getCsrfToken: () => "csrf%2Dvalue",
    fetchImpl: async (_url, request) => {
      options = request;
      return response(
        {
          error: {
            code: "insufficient_funds",
            message: "Operation would overdraw the account",
          },
        },
        409,
      );
    },
  });
  await assert.rejects(
    client.request("/transactions", {
      method: "POST",
      body: { amount: "10.00" },
    }),
    { message: "Operation would overdraw the account", status: 409 },
  );
  assert.equal(options.headers["X-CSRF-Token"], "csrf-value");
});

test("network failure leaves caller draft unmodified and does not retry financial writes", async () => {
  let attempts = 0;
  const body = { amount: "15.50", description: "Keep this draft" };
  const client = createHttpClient({
    fetchImpl: async () => {
      attempts++;
      throw new TypeError("Network disconnected");
    },
  });
  await assert.rejects(
    client.request("/transactions", { method: "POST", body }),
    { status: 0 },
  );
  assert.equal(attempts, 1);
  assert.deepEqual(body, { amount: "15.50", description: "Keep this draft" });
});

test("wrong confirmation password does not rotate or clear a valid session", async () => {
  let requests = 0;
  const sessions = [];
  const client = createHttpClient({
    onSession: (user) => sessions.push(user),
    fetchImpl: async () => {
      requests++;
      return response(
        { error: { code: "invalid_credentials", message: "Invalid password" } },
        401,
      );
    },
  });
  await assert.rejects(
    client.request("/auth/password", {
      method: "POST",
      body: {
        current_password: "wrong",
        new_password: "another-test-password",
      },
    }),
    { code: "invalid_credentials" },
  );
  assert.equal(requests, 1);
  assert.deepEqual(sessions, []);
});

for (const status of [200, 401]) {
  test(`delayed ${status} from account A is rejected after signing into B without replay`, async () => {
    let release;
    const calls = [];
    const client = createHttpClient({
      fetchImpl: async (url, options) => {
        calls.push([url, options.headers.Authorization]);
        if (url.endsWith("/login")) {
          const account = JSON.parse(options.body).account;
          return response({ access_token: account, user: { id: account } });
        }
        if (url.endsWith("/logout")) return response(null, 204);
        return new Promise((resolve) => {
          release = () => resolve(response({ owner: "A" }, status));
        });
      },
    });
    await client.authenticate("/auth/login", { account: "A" });
    const pending = client.request("/accounts", {
      method: "POST",
      body: { name: "A private account" },
    });
    const rejected = assert.rejects(pending, { code: "session_changed" });
    await client.logout();
    await client.authenticate("/auth/login", { account: "B" });
    release();
    await rejected;
    assert.deepEqual(
      calls.filter(([url]) => url.endsWith("/accounts")),
      [["/api/v1/accounts", "Bearer A"]],
    );
    assert.equal(
      calls.some(([url]) => url.endsWith("/refresh")),
      false,
    );
  });
  test(`delayed retry ${status} cannot return data or clear a newer session`, async () => {
    let release;
    let announceRetry;
    const retryStarted = new Promise((resolve) => {
      announceRetry = resolve;
    });
    const sessions = [];
    const client = createHttpClient({
      onSession: (user) => sessions.push(user),
      fetchImpl: async (url, options) => {
        if (url.endsWith("/login")) {
          const account = JSON.parse(options.body).account;
          return response({ access_token: account, user: { id: account } });
        }
        if (url.endsWith("/refresh"))
          return response({ access_token: "A-rotated", user: { id: "A" } });
        if (options.headers.Authorization === "Bearer A")
          return response({}, 401);
        announceRetry();
        return new Promise((resolve) => {
          release = () => resolve(response({ owner: "A" }, status));
        });
      },
    });
    await client.authenticate("/auth/login", { account: "A" });
    const pending = client.request("/accounts");
    const rejected = assert.rejects(pending, { code: "session_changed" });
    await retryStarted;
    await client.authenticate("/auth/login", { account: "B" });
    release();
    await rejected;
    assert.equal(sessions.at(-1).id, "B");
  });
}
