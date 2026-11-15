import test from 'node:test';
import assert from 'node:assert/strict';
import { decimalInput } from '../src/utils/decimalInput.js';

test('monetary editing strips only insignificant DB padding, never rounds or converts floats', () => {
  assert.equal(decimalInput('1250.000000'), '1250.00');
  assert.equal(decimalInput('999999999.990000'), '999999999.99');
  assert.equal(decimalInput('1.001'), '1.001');
  assert.equal(decimalInput('1.'), '1.');
  assert.equal(decimalInput('0.123456', 6), '0.123456');
  assert.equal(decimalInput(''), '');
});

test('payment and contribution correction routes keep exact amounts and ownership identifiers', async () => {
  const calls = [];
  const original = globalThis.fetch;
  globalThis.fetch = async (url, options) => { calls.push({url, ...options}); return new Response('{}'); };
  const api = await import('../src/services/index.js?audit-finance');
  globalThis.fetch = original;
  await api.updateZakatPayment('p', {amount: '15.50', history_id: 'h'});
  assert.equal(calls.at(-1).url, '/api/v1/zakat/payments/p');
  assert.equal(calls.at(-1).method, 'PATCH');
  assert.equal(JSON.parse(calls.at(-1).body).amount, '15.50');
  await api.deleteZakatPayment('p');
  assert.equal(calls.at(-1).method, 'DELETE');
  await api.updateGoalContribution('g', 'c', {amount: '1250.00'});
  assert.equal(calls.at(-1).url, '/api/v1/goals/g/contributions/c');
  assert.equal(calls.at(-1).method, 'PATCH');
  await api.deleteGoalContribution('g', 'c');
  assert.equal(calls.at(-1).method, 'DELETE');
});
