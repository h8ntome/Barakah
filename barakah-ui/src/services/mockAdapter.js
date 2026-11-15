import {
  zakatProfile, dashboard, portfolio, investmentEducation, causes,
  advisorExamples, fallbackReply, welcomeMessage, starterQuestions,
} from '../mocks/data.js';
import { estimateZakat, validateAssets, validGift } from '../utils/finance.js';

// Legacy mock-only fixture adapter; never selected by the running app.
export function createMockAdapter({ delay = 420, failOnce = [], empty = [] } = {}) {
  let profile = structuredClone(zakatProfile);
  let sequence = 0;
  const failures = new Set(failOnce);
  async function request(operation, action) {
    await new Promise(resolve => setTimeout(resolve, delay));
    if (failures.delete(operation)) {
      const error = new Error('The demo request did not complete. Your changes are safe to retry.');
      error.code = 'MOCK_UNAVAILABLE';
      throw error;
    }
    return structuredClone(action());
  }
  return {
    getDashboard: () => request('getDashboard', () => ({
      ...dashboard, summary: estimateZakat(profile.assets, profile.illustrativeRate),
    })),
    getZakatProfile: () => request('getZakatProfile', () => profile),
    saveZakatProfile: payload => request('saveZakatProfile', () => {
      if (payload.currency !== 'USD') throw new Error('This prototype supports USD only.');
      validateAssets(payload.assets);
      profile = { ...profile, assets: { ...payload.assets }, updatedAt: new Date().toISOString() };
      return profile;
    }),
    getPortfolio: () => request('getPortfolio', () => empty.includes('portfolio') ? { ...portfolio, value: 0, allocations: [], holdings: [] } : portfolio),
    getInvestmentEducation: () => request('getInvestmentEducation', () => investmentEducation),
    getCauses: (filters = {}) => request('getCauses', () => {
      if (empty.includes('causes')) return [];
      if (filters.category && !['All', 'Education', 'Relief', 'Masjid'].includes(filters.category)) throw new Error('Choose an available category.');
      const query = (filters.query ?? '').trim().toLowerCase();
      return causes.filter(cause => (!filters.category || filters.category === 'All' || cause.category === filters.category) &&
        cause.title.toLowerCase().includes(query));
    }),
    createDonationIntent: payload => request('createDonationIntent', () => {
      if (!causes.some(cause => cause.id === payload.causeId)) throw new Error('Choose an available cause.');
      if (payload.currency !== 'USD' || !validGift(payload.amount)) throw new Error('Enter 1–100,000 USD with up to two decimal places.');
      return { id: 'intent-demo-' + ++sequence, causeId: payload.causeId, amount: payload.amount,
        currency: payload.currency, status: 'demo_confirmed', isDemo: true, paymentProcessed: false, createdAt: new Date().toISOString() };
    }),
    getAdvisorContext: () => request('getAdvisorContext', () => ({ welcomeMessage, starterQuestions })),
    sendAdvisorMessage: payload => request('sendAdvisorMessage', () => {
      if (typeof payload.text !== 'string' || !payload.text.trim() || payload.text.length > 1000) throw new Error('Write a question of 1–1,000 characters.');
      return { id: 'message-demo-' + ++sequence, role: 'assistant',
        text: advisorExamples.find(example => example.keywords.test(payload.text))?.text ?? fallbackReply,
        isDemo: true, createdAt: new Date().toISOString() };
    }),
  };
}
