import test from "node:test";
import assert from "node:assert/strict";
import {
  createZakatDraft,
  validatePaymentHistory,
} from "../src/utils/zakatDraft.js";
test("loading and editing gold never changes a separate nonzero silver amount", () => {
  const saved = {
    currency: "USD",
    assets: {
      cash: "0.00",
      investments: "0.00",
      gold: "100.00",
      silver: "200.00",
      business: "0.00",
      liabilities: "0.00",
    },
  };
  const draft = createZakatDraft(saved, "2026-01-15");
  draft.assets.gold = "150.00";
  assert.equal(draft.assets.silver, "200.00");
  assert.equal(saved.assets.gold, "100.00");
  assert.equal(createZakatDraft(null, "2026-01-15").assets.silver, "0.00");
  const legacy = { ...saved, assets: { ...saved.assets, silver: undefined } };
  assert.equal(createZakatDraft(legacy, "2026-01-15").assets.silver, "0.00");
});
test("missing or currency-mismatched payment history cannot silently be submitted", () => {
  const choices = [{ id: "selected", estimate: { currency: "USD" } }];
  assert.doesNotThrow(() => validatePaymentHistory(choices, "USD", "selected"));
  assert.throws(
    () => validatePaymentHistory([], "USD", "selected"),
    /selected calculation is unavailable/,
  );
  assert.throws(
    () => validatePaymentHistory(choices, "EUR", "selected"),
    /selected calculation is unavailable/,
  );
  assert.doesNotThrow(() => validatePaymentHistory([], "USD", ""));
});
