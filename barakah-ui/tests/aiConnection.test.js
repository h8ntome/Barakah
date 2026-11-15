import test from "node:test";
import assert from "node:assert/strict";
import { createHttpClient } from "../src/services/httpClient.js";

const calls = [];
const original = globalThis.fetch;
globalThis.fetch = async (url, options) => {
  calls.push({ url, ...options });
  return new Response(JSON.stringify({ mode: "external", has_key: true, user: { id: "owner", ai_consent: false } }));
};
const api = await import("../src/services/index.js");
globalThis.fetch = original;

test("connection mutations preflight auth, use revision-guarded routes and update saved consent", async () => {
  const body = { mode: "external", provider: "openai", model_id: "synthetic-model", api_key: "synthetic-key-not-real", expected_revision: null };
  await api.saveAIConnection(body);
  assert.equal(calls.at(-2).url, "/api/v1/auth/me");
  assert.equal(calls.at(-1).method, "PUT");
  assert.deepEqual(JSON.parse(calls.at(-1).body), body);
  assert.equal(api.getSession().ai_consent, false);
  await api.testAIConnection("revision");
  assert.equal(calls.at(-2).url, "/api/v1/auth/me");
  assert.equal(calls.at(-1).url, "/api/v1/ai/connection/test");
  assert.deepEqual(JSON.parse(calls.at(-1).body), { expected_revision: "revision" });
  await api.removeAIConnection("revision");
  assert.equal(calls.at(-1).method, "DELETE");
  assert.deepEqual(JSON.parse(calls.at(-1).body), { expected_revision: "revision" });
});

for (const code of ["ai_invalid_key", "ai_provider_limited", "ai_model_rejected", "ai_setup_required", "ai_credentials_unavailable"]) {
  test(`${code} displays the backend's sanitized actionable error without automatic retries`, async () => {
    let attempts = 0;
    const client = createHttpClient({ fetchImpl: async () => {
      attempts++;
      return new Response(JSON.stringify({ error: { code, message: "Safe actionable explanation" } }), { status: 503 });
    }});
    await assert.rejects(client.request("/ai/connection/test", { method: "POST", retryAuth: false }), { code, message: "Safe actionable explanation" });
    assert.equal(attempts, 1);
  });
}
