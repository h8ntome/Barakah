import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";
import { createHttpClient } from "../src/services/httpClient.js";

const source = await readFile(new URL("../src/screens/Chat.jsx", import.meta.url), "utf8");

test("Chat does not claim configured or unavailable before context loads; composer stays usable", async () => {
  const server = await createServer({
    server: { middlewareMode: true }, appType: "custom",
    optimizeDeps: { noDiscovery: true, include: [] },
  });
  try {
    const { default: Chat } = await server.ssrLoadModule("/src/screens/Chat.jsx");
    const html = renderToStaticMarkup(createElement(Chat, {
      user: { ai_consent: false }, navigate: () => {}, active: true,
    }));
    assert.match(html, /AI configuration not yet verified/);
    assert.doesNotMatch(html, /AI endpoint configured|AI assistant unavailable/);
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
  assert.match(source, /AI assistant unavailable — no model is connected/);
  assert.match(source, /no advice is generated and no new messages are saved/);
  assert.match(source, /onClick=\{\(\) => setText\(question\)\}/);
  assert.match(source, /Historical conversation only/);
  assert.match(source, /Historical demonstration · Not AI advice/);
  assert.match(source, /Model response · May be inaccurate, not authoritative/);
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


test("Settings explains saved opt-in consent without claiming a connection", async () => {
  const settings = await readFile(new URL("../src/screens/Settings.jsx", import.meta.url), "utf8");
  assert.match(settings, /I consent to sending my questions and recent conversation history/);
  assert.match(settings, /Save settings before sending/);
  assert.match(settings, /Consent does not connect a model/);
  assert.match(settings, /when AI is unavailable, no text is sent or saved/);
});

test("Configured status is not readiness and model content remains plain React text", () => {
  assert.match(source, /context.data\?\.status === "configured"/);
  assert.match(source, /availability is checked on send/);
  assert.match(source, /Save consent in Settings first/);
  assert.match(source, /never your financial records automatically/);
  assert.match(source, /Model suggestions are not Sharia-screened/);
  assert.match(source, /Verify calculations independently/);
  assert.match(source, /\{message.text\}/);
  assert.doesNotMatch(source, /dangerouslySetInnerHTML|marked|innerHTML/);
});

test("AI timeouts preserve the draft and sends never auto-retry even after 401", async () => {
  const adapter = await readFile(new URL("../src/services/index.js", import.meta.url), "utf8");
  assert.match(adapter, /sendMessage[\s\S]*?retryAuth: false/);
  for (const [status, code, message] of [
    [504, "ai_timeout", "AI request timed out. No message was saved."],
    [401, "unauthorized", "Session expired"],
  ]) {
    let calls = 0;
    const client = createHttpClient({ fetchImpl: async () => {
      calls++;
      return new Response(JSON.stringify({ error: { code, message } }), { status });
    }});
    const draft = { text: "Keep this question" };
    await assert.rejects(client.request("/advisor/messages", {
      method: "POST", body: draft, retryAuth: false,
    }), { status, code, message });
    assert.equal(calls, 1);
    assert.equal(draft.text, "Keep this question");
  }
});
