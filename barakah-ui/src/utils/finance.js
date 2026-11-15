export const assetKeys = ['cash', 'investments', 'gold', 'business'];
export const maxAmount = 999999999.99;

export function validateAssets(assets) {
  if (!assets || typeof assets !== 'object') throw new Error('Enter all five asset and liability amounts.');
  for (const key of [...assetKeys, 'liabilities']) {
    if (typeof assets[key] !== 'number' || !Number.isFinite(assets[key]) || assets[key] < 0 || assets[key] > maxAmount) {
      throw new Error('Amounts must be between 0 and 999,999,999.99 USD.');
    }
    if (Math.abs(assets[key] * 100 - Math.round(assets[key] * 100)) > 0.0001) {
      throw new Error('Use no more than two decimal places.');
    }
  }
  return assets;
}

export function estimateZakat(assets, rate = 0.025) {
  validateAssets(assets);
  const totalCents = assetKeys.reduce((total, key) => total + Math.round(assets[key] * 100), 0);
  const liabilitiesCents = Math.round(assets.liabilities * 100);
  const eligibleCents = Math.max(0, totalCents - liabilitiesCents);
  // Provisional display estimate only: no nisab gating, haul or scholarly methodology.
  return {
    totalAssets: totalCents / 100, liabilities: liabilitiesCents / 100,
    netWorth: (totalCents - liabilitiesCents) / 100,
    eligibleBase: eligibleCents / 100,
    estimatedDue: Math.round(eligibleCents * rate) / 100,
  };
}

export function money(value, currency = 'USD', decimals = false) {
  if (value === null || value === undefined || value === '') return 'Unavailable';
  return new Intl.NumberFormat('en-US', {
    style: 'currency', currency, minimumFractionDigits: decimals || !Number.isInteger(value) ? 2 : 0, maximumFractionDigits: 2,
  }).format(value);
}
export function displayDate(iso) {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' }).format(new Date(iso));
}
export function validGift(amount) {
  return Number.isFinite(amount) && amount >= 1 && amount <= 100000 &&
    Math.abs(amount * 100 - Math.round(amount * 100)) < 0.0001;
}
