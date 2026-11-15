// Test-only observer: preserve native fetch and capture only synthetic advisor responses.
window.__aiEvidence = [];
const originalFetch = window.fetch.bind(window);
window.fetch = async (...args) => {
  const response = await originalFetch(...args);
  if (String(args[0]).endsWith('/advisor/messages')) {
    window.__aiEvidence.push({status: response.status, body: await response.clone().json()});
  }
  return response;
};
