// Explicit UI-only failure fixture, installed before the service captures fetch.
// All other settings requests use the real local API. No request bodies or credentials recorded.
(() => {
  const original = window.fetch.bind(window);
  let failed = false;
  window.__aiSettingsFailureFixture = false;
  window.fetch = async (input, options = {}) => {
    const path = new URL(typeof input === 'string' ? input : input.url, location.href).pathname;
    if (window.__aiSettingsFailureFixture && path.endsWith('/ai/connection/test')) {
      failed = true;
      return new Response(JSON.stringify({ error: {
        code: 'ai_invalid_key', message: 'Synthetic rejection fixture — update your key.',
      } }), { status: 503, headers: { 'Content-Type': 'application/json' } });
    }
    const response = await original(input, options);
    if (window.__aiSettingsFailureFixture && failed && path.endsWith('/ai/connection') && options.method === 'GET') {
      const body = await response.json();
      return new Response(JSON.stringify({ ...body, test_status: 'failed', test_error: 'ai_invalid_key', tested_at: new Date().toISOString() }),
        { status: 200, headers: { 'Content-Type': 'application/json' } });
    }
    return response;
  };
})();
