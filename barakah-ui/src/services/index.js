import { createMockAdapter } from './mockAdapter.js';

// The only adapter-selection point. A future teammate-owned httpAdapter can
// implement the same operations here after API_CONTRACT.md is agreed.
const params = new URLSearchParams(typeof window === 'undefined' ? '' : window.location.search);
/** @type {import('../types/api').ServiceAdapter} */
const adapter = createMockAdapter({
  failOnce: (params.get('mockError') ?? '').split(',').filter(Boolean),
  empty: (params.get('mockEmpty') ?? '').split(',').filter(Boolean),
  delay: params.get('mockSlow') === '1' ? 1800 : 420,
});
export const getDashboard = adapter.getDashboard;
export const getZakatProfile = adapter.getZakatProfile;
export const saveZakatProfile = adapter.saveZakatProfile;
export const getPortfolio = adapter.getPortfolio;
export const getInvestmentEducation = adapter.getInvestmentEducation;
export const getCauses = adapter.getCauses;
export const createDonationIntent = adapter.createDonationIntent;
export const getAdvisorContext = adapter.getAdvisorContext;
export const sendAdvisorMessage = adapter.sendAdvisorMessage;
