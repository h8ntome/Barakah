import test from 'node:test';
import assert from 'node:assert/strict';
import { estimateZakat, money, validateAssets, validGift } from '../src/utils/finance.js';

const assets = { cash: 12000, investments: 10500, gold: 1500, business: 750, liabilities: 0 };

test('default values match Home and Zakat example', () => {
  assert.deepEqual(estimateZakat(assets), { totalAssets: 24750, liabilities: 0, netWorth: 24750, eligibleBase: 24750, estimatedDue: 618.75 });
});
test('liabilities reduce net worth and estimate without making the estimate negative', () => {
  assert.equal(estimateZakat({ ...assets, liabilities: 1000 }).estimatedDue, 593.75);
  const result = estimateZakat({ ...assets, liabilities: 30000 });
  assert.equal(result.netWorth, -5250);
  assert.equal(result.estimatedDue, 0);
});
test('zero assets and fractional-cent zakat are handled in cents', () => {
  assert.equal(estimateZakat({ cash: 0, investments: 0, gold: 0, business: 0, liabilities: 0 }).estimatedDue, 0);
  assert.equal(estimateZakat({ cash: 0.1, investments: 0.2, gold: 0, business: 0, liabilities: 0 }).totalAssets, 0.3);
  assert.equal(estimateZakat({ cash: 100.2, investments: 0, gold: 0, business: 0, liabilities: 0 }).estimatedDue, 2.51);
});
test('asset trust boundary rejects missing, negative, nonfinite and overprecision values', () => {
  for (const value of [-1, Infinity, NaN, '100', 1.001, 1000000000]) assert.throws(() => validateAssets({ ...assets, cash: value }));
  assert.throws(() => validateAssets({ cash: 1 }));
  assert.throws(() => validateAssets(null));
});
test('gift validation has explicit upper/lower limits and cent precision', () => {
  for (const amount of [1, 25, 12.34, 100000]) assert.equal(validGift(amount), true);
  for (const amount of [0, -1, NaN, Infinity, 100001, 1.001]) assert.equal(validGift(amount), false);
});
test('currency display is consistent for whole and fractional amounts', () => {
  assert.equal(money(24750), '$24,750');
  assert.equal(money(618.75), '$618.75');
  assert.equal(money(3315.6), '$3,315.60');
  assert.equal(money(0, 'USD', true), '$0.00');
});
