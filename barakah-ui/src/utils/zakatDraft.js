export function createZakatDraft(initial, valuationDate) {
  const blank = {
    currency: "USD",
    assets: {
      cash: "0.00",
      savings: "0.00",
      other: "0.00",
      investments: "0.00",
      gold: "0.00",
      silver: "0.00",
      business: "0.00",
      liabilities: "0.00",
    },
    nisab_method: "manual",
    manual_nisab: "",
    gold_nisab_grams: "85",
    silver_nisab_grams: "595",
    gold_price_per_gram: "",
    silver_price_per_gram: "",
    price_source: "",
    classification_notes: "",
    valuation_date: valuationDate,
    haul_start: "",
    haul_complete: false,
    rate: "0.025",
  };
  return initial
    ? {
        ...initial,
        classification_notes: initial.classification_notes ?? "",
        gold_nisab_grams: initial.gold_nisab_grams ?? blank.gold_nisab_grams,
        silver_nisab_grams:
          initial.silver_nisab_grams ?? blank.silver_nisab_grams,
        assets: {
          ...initial.assets,
          silver: initial.assets.silver ?? "0.00",
          savings: initial.assets.savings ?? "0.00",
          other: initial.assets.other ?? "0.00",
        },
      }
    : blank;
}
export function validatePaymentHistory(histories, currency, historyId) {
  if (
    historyId &&
    !histories.some(
      (item) => item.id === historyId && item.estimate.currency === currency,
    )
  ) {
    throw new Error(
      "The selected calculation is unavailable. Reload calculation choices or choose no linked calculation before saving.",
    );
  }
}
