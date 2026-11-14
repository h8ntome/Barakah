// All sample content lives here. Amounts are USD major units, not cents.
export const zakatProfile = {
  id: 'zakat-demo-001', currency: 'USD', updatedAt: '2026-01-15T09:41:00.000Z',
  assets: { cash: 12000, investments: 10500, gold: 1500, business: 750, liabilities: 0 },
  illustrativeNisab: 6380, illustrativeRate: 0.025, isDemo: true,
};
export const dashboard = {
  id: 'dashboard-demo-001', displayName: 'Hadi', currency: 'USD', isDemo: true,
  sampleChangePercent: 4.2, samplePeriodDays: 30,
  insight: 'A little, regularly. Set aside a small amount for giving when you plan your monthly budget.',
  trend: [12, 18, 17, 29, 25, 38, 34, 46, 44, 57],
};
export const portfolio = {
  id: 'portfolio-demo-001', currency: 'USD', value: 18420,
  sampleChangePercent: 6.8, samplePeriodDays: 30, isDemo: true,
  screeningStatus: 'unverified', trend: [12, 19, 17, 26, 33, 30, 44, 42, 56],
  allocations: [
    { id: 'diversified', label: 'Diversified', percent: 40, color: '#0B7750' },
    { id: 'healthcare', label: 'Healthcare', percent: 20, color: '#549EAD' },
    { id: 'consumer', label: 'Consumer', percent: 18, color: '#9CCFAE' },
    { id: 'energy', label: 'Energy', percent: 12, color: '#D5B669' },
    { id: 'other', label: 'Other', percent: 10, color: '#BAC9BF' },
  ],
  holdings: [
    { id: 'holding-demo-001', name: 'Cedar Growth Basket', category: 'Diversified', value: 7368, isFictional: true },
    { id: 'holding-demo-002', name: 'Olive Healthcare Basket', category: 'Healthcare', value: 3684, isFictional: true },
    { id: 'holding-demo-003', name: 'Noor Consumer Basket', category: 'Consumer', value: 3315.6, isFictional: true },
  ],
};
export const investmentEducation = [
  { id: 'business-activities', title: 'Start with the business', description: 'Understand how a company earns its money. Review activities and revenue sources against a reputable Sharia screening method.' },
  { id: 'financial-ratios', title: 'Look beyond the label', description: 'Debt, interest income and other financial ratios matter. Thresholds and calculation methods differ between screening providers.' },
  { id: 'ongoing-monitoring', title: 'Keep checking in', description: 'A screening result can change as a business and its financial statements change. Use current information and qualified guidance.' },
];
export const causes = [
  { id: 'cause-water', title: 'Provide Clean Water', category: 'Relief', raised: 3420, goal: 5000, currency: 'USD', illustration: 'water', description: 'An illustrative project to bring safe, reliable drinking water closer to families. This is not a verified charity or active campaign.', isDemo: true },
  { id: 'cause-orphans', title: 'Support Orphans', category: 'Education', raised: 7800, goal: 10000, currency: 'USD', illustration: 'care', description: 'An illustrative fund for learning materials and everyday care for children. No real beneficiaries or organizations are represented.', isDemo: true },
  { id: 'cause-masjid', title: 'Build a Masjid', category: 'Masjid', raised: 12500, goal: 20000, currency: 'USD', illustration: 'masjid', description: 'Imagine contributing to an accessible, welcoming community prayer space. This is a fictional project for demonstration only.', isDemo: true },
  { id: 'cause-school', title: 'School Supplies', category: 'Education', raised: 1900, goal: 4000, currency: 'USD', illustration: 'school', description: 'An illustrative project for books, stationery and classroom essentials. No real donation will be made.', isDemo: true },
];
export const starterQuestions = ['How do I calculate zakat?', 'What makes a stock halal?', 'Help me create a savings plan'];
export const welcomeMessage = {
  id: 'message-welcome', role: 'assistant', createdAt: '2026-01-15T09:41:00.000Z', isDemo: true,
  text: 'Assalamu Alaikum! I’m your Barakah guide. Let’s explore budgeting, zakat, sadaqah, and Sharia-conscious investing, one question at a time.',
};
export const advisorExamples = [
  { keywords: /zakat|nisab/i, text: 'A common starting point is 2.5% of eligible wealth, subject to nisab and a lunar holding period. Asset categories and debt treatment vary by scholarly method. The Zakat tab shows a simplified estimate, not a definitive ruling. Consult a qualified scholar for your circumstances.' },
  { keywords: /stock|halal|sharia|invest|portfolio/i, text: 'Review both business activities and financial ratios using a reputable, current Sharia screening methodology. Standards differ, and status can change. Explore the Invest tab to learn the questions to ask. This demo does not certify securities or recommend trades.' },
  { keywords: /sav|budget|spend|expense|income|plan/i, text: 'Start with a simple monthly plan: list income, essential expenses, a manageable savings amount and voluntary giving. Build an emergency buffer before taking investment risk. Review your plan each month and adjust it to what is realistic for you.' },
  { keywords: /sadaqah|charity|donat|giv/i, text: 'Sadaqah is voluntary giving. Choose a manageable amount and a cause you care about, then verify the organization before giving. It is separate from zakat eligibility. The Give tab lets you explore a demo intention only; no payment takes place.' },
];
export const fallbackReply = 'I can share local examples about budgeting, zakat, sadaqah and Sharia-conscious investing. I don’t access accounts or use a live AI model. Try one of those topics, and don’t share sensitive financial information. For personal financial or religious decisions, seek qualified advice.';
