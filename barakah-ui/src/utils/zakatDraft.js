export function createZakatDraft(initial, valuationDate) {
  const blank = {
    currency: "USD",
    assets: {
      cash: "0.00",
      investments: "0.00",
      gold: "0.00",
      silver: "0.00",
      business: "0.00",
      liabilities: "0.00",
    },
    nisab_method: "manual",
    manual_nisab: "",
    gold_price_per_gram: "",
    silver_price_per_gram: "",
    price_source: "",
    valuation_date: valuationDate,
    haul_start: "",
    haul_complete: false,
    rate: "0.025",
  };
  return initial
    ? {
        ...initial,
        assets: { ...initial.assets, silver: initial.assets.silver ?? "0.00" },
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
