// Legacy mock-only regression tests. The production UI does not import this adapter.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createMockAdapter } from '../src/services/mockAdapter.js';

const adapter = options => createMockAdapter({ delay: 0, ...options });

test('requests are asynchronous and return isolated JSON-ready copies', async () => {
  const api = adapter();
  let settled = false;
  const request = api.getZakatProfile().then(data => { settled = true; return data; });
  assert.equal(settled, false);
  const first = await request;
  first.assets.cash = 0;
  assert.equal((await api.getZakatProfile()).assets.cash, 12000);
  assert.deepEqual(JSON.parse(JSON.stringify(first)), first);
});
test('saving updates profile and dashboard coherently', async () => {
  const api = adapter();
  const profile = await api.getZakatProfile();
  await api.saveZakatProfile({ currency: 'USD', assets: { ...profile.assets, cash: 13000 } });
  const dashboard = await api.getDashboard();
  assert.equal(dashboard.summary.netWorth, 25750);
  assert.equal(dashboard.summary.estimatedDue, 643.75);
});
test('failed save preserves prior data and retry saves once', async () => {
  const api = adapter({ failOnce: ['saveZakatProfile'] });
  const profile = await api.getZakatProfile();
  const payload = { currency: 'USD', assets: { ...profile.assets, cash: 9000 } };
  await assert.rejects(api.saveZakatProfile(payload), { code: 'MOCK_UNAVAILABLE' });
  assert.equal((await api.getZakatProfile()).assets.cash, 12000);
  assert.equal((await api.saveZakatProfile(payload)).assets.cash, 9000);
});
test('invalid saves cannot mutate data', async () => {
  const api = adapter();
  const profile = await api.getZakatProfile();
  await assert.rejects(api.saveZakatProfile({ currency: 'PKR', assets: profile.assets }));
  await assert.rejects(api.saveZakatProfile({ currency: 'USD', assets: { ...profile.assets, cash: -1 } }));
  assert.deepEqual(await api.getZakatProfile(), profile);
});
test('cause search combines category with trimmed, case-insensitive query', async () => {
  const api = adapter();
  assert.equal((await api.getCauses()).length, 4);
  assert.deepEqual((await api.getCauses({ category: 'Education', query: ' SCHOOL ' })).map(cause => cause.id), ['cause-school']);
  assert.equal((await api.getCauses({ category: 'Relief', query: 'school' })).length, 0);
  await assert.rejects(api.getCauses({ category: 'Unknown' }));
});
test('empty states are deterministic and do not leak between adapters', async () => {
  const api = adapter({ empty: ['causes', 'portfolio'] });
  assert.deepEqual(await api.getCauses(), []);
  assert.deepEqual((await api.getPortfolio()).holdings, []);
  assert.equal((await adapter().getCauses()).length, 4);
});
test('donations are explicitly demo-only with validation', async () => {
  const api = adapter();
  const intent = await api.createDonationIntent({ causeId: 'cause-water', amount: 25, currency: 'USD' });
  assert.equal(intent.status, 'demo_confirmed');
  assert.equal(intent.paymentProcessed, false);
  assert.equal(intent.isDemo, true);
  await assert.rejects(api.createDonationIntent({ causeId: 'unknown', amount: 25, currency: 'USD' }));
  await assert.rejects(api.createDonationIntent({ causeId: 'cause-water', amount: 0, currency: 'USD' }));
});
test('all three starter questions receive deterministic, relevant examples', async () => {
  const api = adapter();
  const context = await api.getAdvisorContext();
  assert.equal(context.starterQuestions.length, 3);
  for (const [index, text] of context.starterQuestions.entries()) {
    const reply = await api.sendAdvisorMessage({ text });
    assert.match(reply.text, [/nisab/, /business activities/, /monthly plan/][index]);
    assert.equal(reply.isDemo, true);
    assert.equal(reply.text, (await api.sendAdvisorMessage({ text })).text);
  }
  await assert.rejects(api.sendAdvisorMessage({ text: '  ' }));
  await assert.rejects(api.sendAdvisorMessage({ text: 'x'.repeat(1001) }));
  assert.match((await api.sendAdvisorMessage({ text: 'unrelated question' })).text, /don’t share sensitive/);
});
test('portfolio allocation totals 100 and real securities are not certified', async () => {
  const portfolio = await adapter().getPortfolio();
  assert.equal(portfolio.allocations.reduce((sum, item) => sum + item.percent, 0), 100);
  assert.equal(portfolio.screeningStatus, 'unverified');
  assert.ok(portfolio.holdings.every(holding => holding.isFictional));
});
test('every operation supports a recoverable injected failure', async () => {
  const operations = ['getDashboard', 'getZakatProfile', 'getPortfolio', 'getInvestmentEducation', 'getCauses', 'getAdvisorContext'];
  const api = adapter({ failOnce: operations });
  for (const name of operations) {
    await assert.rejects(api[name](), { code: 'MOCK_UNAVAILABLE' });
    assert.ok(await api[name]());
  }
});
