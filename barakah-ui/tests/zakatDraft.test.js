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

test("legacy zakat profiles gain independent savings/other and configurable nisab weight defaults", () => {
  const initial = {
    currency: "USD",
    assets: { cash: "123.45", gold: "20.00" },
  };
  const draft = createZakatDraft(initial, "2026-01-15");
  assert.equal(draft.assets.cash, "123.45");
  assert.equal(draft.assets.savings, "0.00");
  assert.equal(draft.assets.other, "0.00");
  assert.equal(draft.gold_nisab_grams, "85");
  assert.equal(draft.silver_nisab_grams, "595");
  assert.equal(draft.classification_notes, "");
  draft.assets.savings = "100.00";
  assert.equal(draft.assets.cash, "123.45");
  assert.equal(initial.assets.savings, undefined);
});
test("saved savings/other and six-decimal methodology weights survive draft initialization exactly", () => {
  const initial = {
    currency: "USD",
    assets: {
      cash: "1.00",
      savings: "1200.30",
      other: "42.20",
      silver: "10.00",
    },
    gold_nisab_grams: "87.480001",
    silver_nisab_grams: "612.360001",
    classification_notes: "Jewelry excluded under my chosen interpretation",
  };
  assert.deepEqual(createZakatDraft(initial, "2026-01-15"), initial);
  const blank = createZakatDraft(null, "2026-01-15");
  assert.equal(blank.assets.savings, "0.00");
  assert.equal(blank.assets.other, "0.00");
  assert.equal(blank.gold_nisab_grams, "85");
  assert.equal(blank.silver_nisab_grams, "595");
});
