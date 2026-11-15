import { createHttpClient, queryString } from "./httpClient.js";
const listeners = new Set();
let currentUser = null;
export const client = createHttpClient({
  baseUrl: import.meta.env?.VITE_API_BASE_URL || "/api/v1",
  onSession: (user) => {
    currentUser = user;
    listeners.forEach((listener) => listener(user));
  },
});
export const subscribeSession = (listener) => {
  listeners.add(listener);
  return () => listeners.delete(listener);
};
export const getSession = () => currentUser;
export const setSessionUser = (user) => {
  currentUser = user;
  listeners.forEach((listener) => listener(user));
};
const get = (path, filters) => client.request(path + queryString(filters));
const post = (path, body) => client.request(path, { method: "POST", body });
const patch = (path, body) => client.request(path, { method: "PATCH", body });
const put = (path, body) => client.request(path, { method: "PUT", body });
const del = (path, body) => client.request(path, { method: "DELETE", body });
const id = encodeURIComponent;
export const register = (body) => client.authenticate("/auth/register", body);
export const login = (body) => client.authenticate("/auth/login", body);
export const startDemo = () => client.authenticate("/auth/demo");
export const resetDemo = () => client.replaceSession("/auth/demo/reset");
export const logout = () => client.logout();
export const refreshSession = () => client.refresh();
export const updateProfile = async (body) => {
  const user = await patch("/auth/profile", body);
  setSessionUser(user);
  return user;
};
export const changePassword = async (body) => {
  await client.request("/auth/password", {
    method: "POST",
    body,
  });
  client.clearSession();
};
export const deleteUser = async (body) => {
  await client.request("/auth/me", { method: "DELETE", body });
  client.clearSession();
};
export const requestReset = (body) =>
  client.request("/auth/reset/request", { method: "POST", body, public: true });
export const confirmReset = (body) =>
  client.request("/auth/reset/confirm", { method: "POST", body, public: true });
export const getDashboard = (filters) => get("/dashboard", filters);
export const getAccounts = (filters) => get("/accounts", filters);
export const createAccount = (body) => post("/accounts", body);
export const updateAccount = (accountId, body) =>
  patch(`/accounts/${id(accountId)}`, body);
export const deleteAccount = (accountId) => del(`/accounts/${id(accountId)}`);
export const getTransactions = (filters) => get("/transactions", filters);
export const createTransaction = (body) => post("/transactions", body);
export const updateTransaction = (transactionId, body) =>
  patch(`/transactions/${id(transactionId)}`, body);
export const deleteTransaction = (transactionId) =>
  del(`/transactions/${id(transactionId)}`);
export const createTransfer = (body) => post("/transfers", body);
export const getBudgets = (filters) => get("/budgets", filters);
export const createBudget = (body) => post("/budgets", body);
export const updateBudget = (budgetId, body) =>
  patch(`/budgets/${id(budgetId)}`, body);
export const deleteBudget = (budgetId) => del(`/budgets/${id(budgetId)}`);
export const getZakatProfile = async () => {
  try {
    return await get("/zakat/profile");
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
};
export const saveZakatProfile = (body) => put("/zakat/profile", body);
export const getZakatEstimate = async () => {
  try {
    return await get("/zakat/estimate");
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
};
export const getZakatHistory = (filters) => get("/zakat/history", filters);
export const saveZakatHistory = () => post("/zakat/history");
export const getZakatPayments = (filters) => get("/zakat/payments", filters);
export const createZakatPayment = (body) => post("/zakat/payments", body);
export const updateZakatPayment = (paymentId, body) => patch(`/zakat/payments/${id(paymentId)}`, body);
export const deleteZakatPayment = (paymentId) => del(`/zakat/payments/${id(paymentId)}`);
export const getCauses = (filters) => get("/causes", filters);
export const getDonations = (filters) => get("/donation-intents", filters);
export const createDonation = (body) => post("/donation-intents", body);
export const getSadaqah = (filters) => get("/sadaqah", filters);
export const createSadaqah = (body) => post("/sadaqah", body);
export const updateSadaqah = (givingId, body) =>
  patch(`/sadaqah/${id(givingId)}`, body);
export const deleteSadaqah = (givingId) => del(`/sadaqah/${id(givingId)}`);
export const getSadaqahSummary = (filters) => get("/sadaqah/summary", filters);
export const getPortfolio = (filters) => get("/portfolio", filters);
export const getPortfolios = (filters) => get("/portfolios", filters);
export const createPortfolio = (body) => post("/portfolios", body);
export const updatePortfolio = (portfolioId, body) =>
  patch(`/portfolios/${id(portfolioId)}`, body);
export const deletePortfolio = (portfolioId) =>
  del(`/portfolios/${id(portfolioId)}`);
export const createHolding = (body) => post("/portfolio/holdings", body);
export const updateHolding = (holdingId, body) =>
  patch(`/portfolio/holdings/${id(holdingId)}`, body);
export const deleteHolding = (holdingId) =>
  del(`/portfolio/holdings/${id(holdingId)}`);
export const updateTrade = (tradeId, body) =>
  patch(`/portfolio/trades/${id(tradeId)}`, body);
export const deleteTrade = (tradeId) => del(`/portfolio/trades/${id(tradeId)}`);
export const getTrades = (filters) => get("/portfolio/trades", filters);
export const createTrade = (body) => post("/portfolio/trades", body);
export const updateQuote = (holdingId, body) =>
  put(`/portfolio/holdings/${id(holdingId)}/quote`, body);
export const updateScreening = (holdingId, body) =>
  put(`/portfolio/holdings/${id(holdingId)}/screening`, body);
export const getInvestmentEducation = () => get("/education/investing");
export const getAdvisorContext = () => get("/advisor/context");
export const getAIConnection = () => get("/ai/connection");
async function changeAIConnection(method, body) {
  const result = await client.request("/ai/connection", {
    method, body, preflightAuth: true, retryAuth: false,
  });
  setSessionUser(result.user);
  return result;
}
export const saveAIConnection = (body) => changeAIConnection("PUT", body);
export const removeAIConnection = (revision) => changeAIConnection("DELETE", { expected_revision: revision });
export const testAIConnection = (revision) => client.request("/ai/connection/test", {
  method: "POST", body: { expected_revision: revision }, preflightAuth: true, retryAuth: false,
});
export const getConversations = (filters) =>
  get("/advisor/conversations", filters);
export const getMessages = async (conversationId) => {
  if (!conversationId) return [];
  const messages = [];
  let page;
  do {
    page = await get(`/advisor/conversations/${id(conversationId)}/messages`, {
      limit: 100,
      offset: messages.length,
    });
    messages.push(...page);
  } while (page.length === 100);
  return messages;
};
export const sendMessage = (body) => client.request("/advisor/messages", {
  method: "POST", body, preflightAuth: true, retryAuth: false,
});
export const deleteConversation = (conversationId) =>
  del(`/advisor/conversations/${id(conversationId)}`);
export const getAds = (context) => get("/ads", { context });
// Choice lists must include accounts beyond the first history page.
export const getAccountChoices = async () => {
  const accounts = [];
  let page;
  do {
    page = await getAccounts({ limit: 100, offset: accounts.length });
    accounts.push(...page);
  } while (page.length === 100);
  return accounts;
};

export const getPortfolioChoices = async () => {
  const portfolios = [];
  let page;
  do {
    page = await getPortfolios({ limit: 100, offset: portfolios.length });
    portfolios.push(...page);
  } while (page.length === 100);
  return portfolios;
};

export const getGoals = (filters) => get("/goals", filters);
export const createGoal = (body) => post("/goals", body);
export const updateGoal = (goalId, body) => patch(`/goals/${id(goalId)}`, body);
export const deleteGoal = (goalId) => del(`/goals/${id(goalId)}`);
export const getGoalContributions = (goalId, filters) =>
  get(`/goals/${id(goalId)}/contributions`, filters);
export const createGoalContribution = (goalId, body) =>
  post(`/goals/${id(goalId)}/contributions`, body);

export const updateGoalContribution = (goalId, contributionId, body) =>
  patch(`/goals/${id(goalId)}/contributions/${id(contributionId)}`, body);
export const deleteGoalContribution = (goalId, contributionId) =>
  del(`/goals/${id(goalId)}/contributions/${id(contributionId)}`);

export const getZakatHistoryChoices = async () => {
  const history = [];
  let page;
  do {
    page = await getZakatHistory({ limit: 100, offset: history.length });
    history.push(...page);
  } while (page.length === 100);
  return history;
};
export const recordAdEvent = (adId, kind) =>
  post(`/ads/${id(adId)}/events`, { kind });

export const getScreeningHistory = (holdingId, filters) =>
  get(`/portfolio/holdings/${id(holdingId)}/screenings`, filters);
