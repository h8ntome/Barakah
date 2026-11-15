import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
const calls = [];
let responseOverride;
const originalFetch = globalThis.fetch;
globalThis.fetch = async (url, options) => {
  calls.push({
    url,
    method: options.method,
    body: options.body ? JSON.parse(options.body) : undefined,
  });
  const data = responseOverride
    ? responseOverride(url)
    : url.endsWith("/auth/profile")
      ? { id: "user", display_name: "New name" }
      : [];
  return new Response(JSON.stringify(data), { status: 200 });
};
const api = await import("../src/services/index.js");
globalThis.fetch = originalFetch;
const last = () => calls.at(-1);

test("ledger and budget mutations use documented routes and preserve decimals", async () => {
  const body = {
    account_id: "a",
    kind: "expense",
    amount: "12.30",
    category: "food",
    description: "Lunch",
    occurred_on: "2026-01-15",
  };
  await api.createTransaction(body);
  assert.deepEqual(last(), {
    url: "/api/v1/transactions",
    method: "POST",
    body,
  });
  await api.updateTransaction("t", body);
  assert.equal(last().url, "/api/v1/transactions/t");
  assert.equal(last().method, "PATCH");
  assert.equal(last().body.amount, "12.30");
  await api.deleteTransaction("t");
  assert.equal(last().method, "DELETE");
  await api.updateBudget("b", {
    amount: "100.00",
    currency: "USD",
    month: "2026-01",
    category: "food",
  });
  assert.equal(last().url, "/api/v1/budgets/b");
  assert.equal(last().body.amount, "100.00");
});
test("transaction and giving filters reach server and blank filters are omitted", async () => {
  await api.getTransactions({
    query: "tea & coffee",
    category: "",
    start_date: "2026-01-01",
    offset: 50,
    limit: 50,
  });
  assert.equal(
    last().url,
    "/api/v1/transactions?query=tea+%26+coffee&start_date=2026-01-01&offset=50&limit=50",
  );
  await api.getSadaqahSummary({ category: "relief", end_date: "2026-12-31" });
  assert.equal(
    last().url,
    "/api/v1/sadaqah/summary?category=relief&end_date=2026-12-31",
  );
});
test("zakat, quote and screening payloads remain server inputs, never browser arithmetic", async () => {
  const body = {
    currency: "USD",
    assets: {
      cash: "12000.00",
      gold: "0.00",
      silver: "200.25",
      business: "0.00",
      investments: "0.00",
      liabilities: "1000.00",
    },
    rate: "0.025",
    nisab_method: "gold",
    gold_price_per_gram: "80.123456",
    haul_complete: true,
    valuation_date: "2026-01-15",
  };
  await api.saveZakatProfile(body);
  assert.deepEqual(last(), {
    url: "/api/v1/zakat/profile",
    method: "PUT",
    body,
  });
  await api.updateQuote("holding", {
    price: "123.123456",
    as_of: "2026-01-15",
    source: "Manual statement",
  });
  assert.equal(last().body.price, "123.123456");
  await api.updateScreening("holding", {
    prohibited_business: null,
    debt_to_assets: null,
    debt_threshold: "0.30",
  });
  assert.equal(last().body.debt_to_assets, null);
  assert.equal(last().body.debt_threshold, "0.30");
});
test("portfolio creation, trades, chat persistence and ads use real API paths", async () => {
  await api.createPortfolio({ name: "Retirement" });
  assert.equal(last().url, "/api/v1/portfolios");
  await api.createTrade({
    holding_id: "h",
    side: "buy",
    quantity: "1.123456",
    price: "10.000001",
    fees: "0.01",
    traded_on: "2026-01-15",
  });
  assert.equal(last().body.quantity, "1.123456");
  await api.sendMessage({
    text: "Explain nisab",
    conversation_id: "conversation",
  });
  assert.equal(last().url, "/api/v1/advisor/messages");
  await api.getMessages("conversation");
  assert.equal(
    last().url,
    "/api/v1/advisor/conversations/conversation/messages?limit=100&offset=0",
  );
  await api.deleteConversation("conversation");
  assert.equal(last().method, "DELETE");
  await api.getAds("dashboard");
  assert.equal(last().url, "/api/v1/ads?context=dashboard");
});
test("production service selection contains no mock adapter or financial calculations", async () => {
  const source = await readFile(
    new URL("../src/services/index.js", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(
    source,
    /mockAdapter|estimateZakat|localStorage|sessionStorage/,
  );
  for (const file of ["Home", "Zakat", "Invest", "Chat", "Give"]) {
    const screen = await readFile(
      new URL(`../src/screens/${file}.jsx`, import.meta.url),
      "utf8",
    );
    assert.doesNotMatch(screen, /from ['"].*mocks|estimateZakat|parseFloat\(/);
  }
});

test("charitable goals CRUD and contribution history use exact documented payloads", async () => {
  const goal = {
    name: "Community fund",
    currency: "USD",
    target_amount: "1200.50",
    target_date: null,
  };
  await api.createGoal(goal);
  assert.deepEqual(last(), {
    url: "/api/v1/goals",
    method: "POST",
    body: goal,
  });
  await api.getGoals({ offset: 50, limit: 50 });
  assert.equal(last().url, "/api/v1/goals?offset=50&limit=50");
  await api.updateGoal("goal/id", {
    ...goal,
    target_amount: "1500.00",
    target_date: "2027-01-15",
  });
  assert.equal(last().url, "/api/v1/goals/goal%2Fid");
  assert.equal(last().method, "PATCH");
  assert.equal(last().body.target_amount, "1500.00");
  await api.createGoalContribution("goal/id", { amount: "12.30" });
  assert.deepEqual(last(), {
    url: "/api/v1/goals/goal%2Fid/contributions",
    method: "POST",
    body: { amount: "12.30" },
  });
  await api.getGoalContributions("goal/id", { offset: 50, limit: 50 });
  assert.equal(
    last().url,
    "/api/v1/goals/goal%2Fid/contributions?offset=50&limit=50",
  );
  await api.deleteGoal("goal/id");
  assert.equal(last().url, "/api/v1/goals/goal%2Fid");
  assert.equal(last().method, "DELETE");
});
test("payment history choices include all pages and remain independent of displayed history pagination", async () => {
  const firstPage = Array.from({ length: 100 }, (_, index) => ({
    id: `h${index}`,
    estimate: { currency: "USD" },
  }));
  responseOverride = (url) =>
    url.includes("offset=100")
      ? [{ id: "last", estimate: { currency: "USD" } }]
      : url.includes("offset=50")
        ? firstPage.slice(50)
        : firstPage;
  try {
    const choices = await api.getZakatHistoryChoices();
    assert.equal(choices.length, 101);
    const selected = choices[0].id;
    const displayed = await api.getZakatHistory({ limit: 50, offset: 50 });
    assert.equal(
      displayed.some((item) => item.id === selected),
      false,
    );
    assert.equal(
      choices.some((item) => item.id === selected),
      true,
    );
    const screen = await readFile(
      new URL("../src/screens/Zakat.jsx", import.meta.url),
      "utf8",
    );
    assert.match(screen, /histories=\{historyChoices\.data \|\| \[\]\}/);
  } finally {
    responseOverride = undefined;
  }
});
test("sponsored impressions and clicks use the event API without client financial targeting", async () => {
  for (const kind of ["impression", "click"]) {
    await api.recordAdEvent("ad/id", kind);
    assert.deepEqual(last(), {
      url: "/api/v1/ads/ad%2Fid/events",
      method: "POST",
      body: { kind },
    });
  }
});
