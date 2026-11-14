/** Draft frontend contract, NOT an established server API. See API_CONTRACT.md.
 * All monetary numbers are major currency units (USD dollars, not cents).
 * ISO 8601 UTC timestamps; stable string IDs; percentages use 0–100,
 * except illustrativeRate, a fraction (0.025).
 */
export type Currency = 'USD'; // Prototype only; agree PKR/FX support with backend.
export type ISODateTime = string;
export interface Assets {
  cash: number; investments: number; gold: number; business: number; liabilities: number;
}
export interface Estimate {
  totalAssets: number; liabilities: number; netWorth: number;
  eligibleBase: number; estimatedDue: number;
}
export interface ZakatProfile {
  id: string; currency: Currency; assets: Assets; updatedAt: ISODateTime;
  illustrativeNisab: number; illustrativeRate: number; isDemo: boolean;
}
export interface ZakatPayload { currency: Currency; assets: Assets }
export interface Dashboard {
  id: string; displayName: string; currency: Currency; isDemo: boolean;
  sampleChangePercent: number; samplePeriodDays: number; insight: string;
  trend: number[]; summary: Estimate;
}
export interface Allocation { id: string; label: string; percent: number; color: string }
export interface Holding {
  id: string; name: string; category: string; value: number; isFictional: boolean;
}
export interface Portfolio {
  id: string; currency: Currency; value: number; sampleChangePercent: number;
  samplePeriodDays: number; isDemo: boolean; screeningStatus: 'unverified';
  trend: number[]; allocations: Allocation[]; holdings: Holding[];
}
export interface EducationItem { id: string; title: string; description: string }
export type CauseCategory = 'All' | 'Education' | 'Relief' | 'Masjid';
export interface CauseFilters { category?: CauseCategory; query?: string }
export interface Cause {
  id: string; title: string; category: Exclude<CauseCategory, 'All'>;
  raised: number; goal: number; currency: Currency;
  illustration: 'water' | 'care' | 'masjid' | 'school';
  description: string; isDemo: boolean;
}
export interface DonationPayload { causeId: string; amount: number; currency: Currency }
export interface DonationIntent extends DonationPayload {
  id: string; status: 'demo_confirmed'; isDemo: true;
  paymentProcessed: false; createdAt: ISODateTime;
}
export interface AdvisorMessage {
  id: string; role: 'assistant' | 'user'; text: string;
  createdAt: ISODateTime; isDemo: boolean;
}
export interface AdvisorPayload { text: string; conversationId?: string }
export interface AdvisorContext { welcomeMessage: AdvisorMessage; starterQuestions: string[] }
export interface ServiceAdapter {
  getDashboard(): Promise<Dashboard>;
  getZakatProfile(): Promise<ZakatProfile>;
  saveZakatProfile(payload: ZakatPayload): Promise<ZakatProfile>;
  getPortfolio(): Promise<Portfolio>;
  getInvestmentEducation(): Promise<EducationItem[]>;
  getCauses(filters?: CauseFilters): Promise<Cause[]>;
  createDonationIntent(payload: DonationPayload): Promise<DonationIntent>;
  getAdvisorContext(): Promise<AdvisorContext>;
  sendAdvisorMessage(payload: AdvisorPayload): Promise<AdvisorMessage>;
}
