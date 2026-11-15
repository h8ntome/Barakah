import test from "node:test";
import assert from "node:assert/strict";
const response = (body, status = 200) =>
  new Response(body === null ? null : JSON.stringify(body), { status });

test("deleteUser refreshes an expired access token and only clears after successful deletion", async () => {
  const originalFetch = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => {
    calls.push([url, options.method, options.headers.Authorization]);
    if (url.endsWith("/login"))
      return response({ access_token: "old", user: { id: "u" } });
    if (url.endsWith("/refresh"))
      return response({ access_token: "new", user: { id: "u" } });
    if (options.headers.Authorization === "Bearer old")
      return response(
        { error: { code: "unauthorized", message: "Expired" } },
        401,
      );
    return response(null, 204);
  };
  let api;
  try {
    api = await import("../src/services/index.js?delete-expired");
  } finally {
    globalThis.fetch = originalFetch;
  }
  await api.login({ email: "test@example.test", password: "test-password" });
  await api.deleteUser({ password: "test-password" });
  assert.deepEqual(calls.slice(1), [
    ["/api/v1/auth/me", "DELETE", "Bearer old"],
    ["/api/v1/auth/refresh", "POST", undefined],
    ["/api/v1/auth/me", "DELETE", "Bearer new"],
  ]);
  assert.equal(api.getSession(), null);
});

test("deleteUser with wrong password preserves session and never refreshes", async () => {
  const originalFetch = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url) => {
    calls.push(url);
    if (url.endsWith("/login"))
      return response({ access_token: "token", user: { id: "u" } });
    return response(
      { error: { code: "invalid_credentials", message: "Invalid password" } },
      401,
    );
  };
  let api;
  try {
    api = await import("../src/services/index.js?delete-wrong-password");
  } finally {
    globalThis.fetch = originalFetch;
  }
  await api.login({ email: "test@example.test", password: "test-password" });
  await assert.rejects(api.deleteUser({ password: "wrong" }), {
    code: "invalid_credentials",
  });
  assert.deepEqual(calls, ["/api/v1/auth/login", "/api/v1/auth/me"]);
  assert.equal(api.getSession().id, "u");
});
