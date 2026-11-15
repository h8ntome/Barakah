import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";
import { createHttpClient } from "../src/services/httpClient.js";

const source = await readFile(new URL("../src/screens/Chat.jsx", import.meta.url), "utf8");

test("Chat renders unavailable notice and usable composer without consent", async () => {
  const server = await createServer({
    server: { middlewareMode: true }, appType: "custom",
    optimizeDeps: { noDiscovery: true, include: [] },
  });
  try {
    const { default: Chat } = await server.ssrLoadModule("/src/screens/Chat.jsx");
    const html = renderToStaticMarkup(createElement(Chat, {
      user: { ai_consent: false }, navigate: () => {}, active: true,
    }));
    assert.match(html, /AI assistant unavailable/);
    assert.match(html, /No messages yet/);
    assert.match(html, /Loading advisor context/);
    const input = html.match(/<input[^>]*aria-label="Message to advisor"[^>]*>/)?.[0];
    assert.ok(input);
    assert.doesNotMatch(input, /disabled/);
    assert.doesNotMatch(html, /Enable advisor consent|configured model|Include my monthly/);
  } finally {
    await server.close();
  }
});

test("Chat preserves draft on errors and labels history and suggestions honestly", () => {
  assert.doesNotMatch(source, /ai_consent|include_financial_context/);
  assert.match(source, /disabled=\{sending \|\| !text.trim\(\)\}/);
  assert.match(source, /Example questions · AI not connected/);
  assert.match(source, /onClick=\{\(\) => setText\(question\)\}/);
  assert.match(source, /Historical conversation only/);
  assert.match(source, /Historical demonstration · Not AI advice/);
  assert.match(source, /Historical model response · May be inaccurate/);
  assert.match(source, /Checking AI availability/);
  assert.match(source, /failure.code === "ai_unavailable"/);
  assert.match(source, /No message was saved/);
  const failureBranch = source.slice(source.indexOf("} catch (failure)"), source.indexOf("} finally"));
  assert.doesNotMatch(failureBranch, /setText|setConversationId|retry\(/);
  assert.match(source, /Your draft is kept/);
  assert.match(source, /await api.deleteConversation\(conversationId\)/);
});

test("AI unavailable envelope rejects exactly once without changing the draft", async () => {
  let calls = 0;
  const client = createHttpClient({
    fetchImpl: async () => {
      calls++;
      return new Response(JSON.stringify({
        conversation_id: null, response: null,
        error: { code: "ai_unavailable", message: "AI is not connected." },
      }), { status: 503 });
    },
  });
  const draft = { text: "My question" };
  await assert.rejects(client.request("/advisor/messages", { method: "POST", body: draft }), {
    code: "ai_unavailable", status: 503,
  });
  assert.equal(calls, 1);
  assert.deepEqual(draft, { text: "My question" });
});


test("Settings labels legacy AI consent as inactive, not a connected provider", async () => {
  const settings = await readFile(new URL("../src/screens/Settings.jsx", import.meta.url), "utf8");
  assert.match(settings, /Saved advisor consent preference \(inactive\)/);
  assert.match(settings, /does not connect a model or enable replies/);
  assert.doesNotMatch(settings, /question may be sent to the|configured model/);
});
