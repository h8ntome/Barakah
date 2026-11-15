import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const calls = [];
const originalFetch = globalThis.fetch;
globalThis.fetch = async (url, options) => {
  calls.push({ url, method: options.method, body: options.body && JSON.parse(options.body) });
  return new Response(JSON.stringify([]), { status: 200 });
};
const api = await import("../src/services/index.js");
globalThis.fetch = originalFetch;
const last = () => calls.at(-1);

test("holding metadata and deletion target owner-scoped API routes", async () => {
  const body = { name: "Corrected name", symbol: "TEST" };
  await api.updateHolding("holding/id", body);
  assert.deepEqual(last(), { url: "/api/v1/portfolio/holdings/holding%2Fid", method: "PATCH", body });
  await api.deleteHolding("holding/id");
  assert.equal(last().url, "/api/v1/portfolio/holdings/holding%2Fid");
  assert.equal(last().method, "DELETE");
});

test("trade corrections retain decimal strings and history carries portfolio filter", async () => {
  const body = { side: "buy", quantity: "12.000001", price: "50.123456", fees: "0.01", traded_on: "2026-01-01" };
  await api.updateTrade("trade/id", body);
  assert.deepEqual(last(), { url: "/api/v1/portfolio/trades/trade%2Fid", method: "PATCH", body });
  await api.deleteTrade("trade/id");
  assert.equal(last().url, "/api/v1/portfolio/trades/trade%2Fid");
  assert.equal(last().method, "DELETE");
  await api.getTrades({ portfolio_id: "p", limit: 50, offset: 0 });
  assert.equal(last().url, "/api/v1/portfolio/trades?portfolio_id=p&limit=50&offset=0");
  await api.updateQuote("h", { price: "0.000000", as_of: "2026-01-01", source: "Manual" });
  assert.equal(last().body.price, "0.000000");
});

test("Invest and PortfolioForms expose explicit confirmations and safe correction constraints", async () => {
  const invest = await readFile(new URL("../src/screens/Invest.jsx", import.meta.url), "utf8");
  const forms = await readFile(new URL("../src/screens/PortfolioForms.jsx", import.meta.url), "utf8");
  assert.match(invest, /holding\.quote_price \?\? ""/);
  assert.match(invest, /api\.getTrades, \{ offset, limit: 50, portfolio_id: portfolioId \}/);
  assert.match(invest, /setPortfolioId\(id\);\s+setOffset\(0\)/);
  assert.match(forms, /Legacy trade: correction and removal unavailable/);
  assert.match(forms, /if \(!trade\.can_correct\)/);
  assert.match(forms, /I confirm removal of this tracked holding and all its trade and screening records/);
  assert.match(forms, /if \(!confirmed\) throw new Error/g);
  assert.match(forms, /max=\{today\(\)\}/);
  assert.doesNotMatch(forms, /parseFloat\(|Number\(draft\.(quantity|price|fees)\)/);
});
