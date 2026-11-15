// Test-only observer, installed before the app captures fetch. No bodies or credentials.
window.__mutationChecks = [];
const sessionTestFetch = window.fetch.bind(window);
window.fetch = async (...args) => {
  const response = await sessionTestFetch(...args);
  if (String(args[0]).endsWith('/accounts') && args[1]?.method === 'POST') {
    window.__mutationChecks.push(response.status);
  }
  return response;
};
