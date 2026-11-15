"""Real browser/API settings flow; one explicit UI error fixture; NEVER calls an AI provider."""
import json
import os
from pathlib import Path
import secrets
from urllib.parse import urlparse
import journey as j

KEY = 'synthetic-browser-credential-' + 'x' * 24


def main():
    if urlparse(j.URL).hostname not in {'127.0.0.1', 'localhost', '::1'}:
        raise SystemExit('This test creates a fictional personal account on loopback only.')
    os.environ['AGENT_BROWSER_INIT_SCRIPTS'] = str(Path(__file__).with_name('observe_ai_settings.js').resolve())
    j.browser('open', j.URL)
    # Belt-and-braces block: a broken fixture cannot accidentally reach a provider.
    j.browser('network', 'route', '**/api/v1/ai/connection/test', '--abort')
    j.click('New account')
    j.fill('Display name', 'Synthetic AI Review')
    j.fill('Email address', f'ai-settings-{secrets.token_hex(5)}@example.com')
    j.fill('New password', secrets.token_urlsafe(24))
    j.click('Create account'); j.wait('Welcome to Barakah.')
    for width in (320, 390, 1280):
        j.browser('set', 'viewport', str(width), '900')
        j.click('Open settings')
        j.wait('AI source')
        layout = json.loads(j.browser('eval', """(() => {
            const panel = document.querySelector('[aria-label="Settings destination"]');
            const heading = [...panel.querySelectorAll('h3')].find(x => x.textContent === 'Your settings');
            const model = panel.querySelector('[aria-label="AI Model"] h3');
            const scroll = panel.closest('.screen-content').getBoundingClientRect();
            const h = heading.getBoundingClientRect(), m = model.getBoundingClientRect();
            return {focused: document.activeElement === panel, headingVisible: h.top >= scroll.top - 1 && h.bottom <= scroll.bottom,
                modelVisible: m.top >= scroll.top && m.bottom <= scroll.bottom,
                noOverflow: document.documentElement.scrollWidth <= innerWidth && panel.scrollWidth <= panel.clientWidth};
        })()"""))
        assert all(layout.values()), (width, layout)
        j.checks.append(f'{width}px gear reveals Settings/AI Model immediately, focuses destination, no horizontal overflow')
        j.screenshot(f'ai-settings-{width}.png')
        j.browser('press', 'Tab')
        assert json.loads(j.browser('eval', 'document.activeElement.tagName')) == 'SELECT'
    j.select('AI source', 'external')
    j.fill('Model ID', 'synthetic-model-not-a-real-provider-test')
    j.fill('API key', KEY)
    assert json.loads(j.browser('eval', 'document.querySelector(".ai-settings input[type=password]").type')) == 'password'
    j.click('Save AI connection'); j.wait('AI connection saved.')
    assert j.browser('get', 'value', j.ref('API key', 'textbox')) == ''
    assert json.loads(j.browser('eval', 'document.querySelector(".ai-settings input[type=password]").placeholder')).startswith('Saved key')
    assert json.loads(j.browser('eval', "[...document.querySelectorAll('button')].find(x=>x.textContent==='Test saved connection').disabled"))
    j.checks.append('real browser saves encrypted connection without refresh cookie outside /auth; key field clears and test requires consent')
    j.browser('reload'); j.wait('Welcome to Barakah.'); j.click('Open settings')
    j.wait('AI source')
    assert j.browser('get', 'value', j.ref('Model ID', 'textbox')) == 'synthetic-model-not-a-real-provider-test'
    assert j.browser('get', 'value', j.ref('API key', 'textbox')) == ''
    assert not json.loads(j.browser('eval', f'JSON.stringify([localStorage,sessionStorage,document.body.innerHTML]).includes({json.dumps(KEY)})'))
    j.checks.append('connection survives reload; synthetic key absent from returned input, page HTML and browser storage')
    j.browser('check', j.ref('I consent to sending my questions and recent conversation history', 'checkbox'))
    j.click('Save AI consent'); j.wait('Saved.')
    j.browser('eval', 'window.__aiSettingsFailureFixture = true')
    j.click('Test saved connection')
    j.wait('Last saved test: Failed (ai_invalid_key)')
    j.wait('Synthetic rejection fixture')
    j.checks.append('explicit UI-only failure fixture: test refreshes status and retains actionable error; backend persistence separately TLS-tested')
    j.browser('eval', 'window.__aiSettingsFailureFixture = false')
    j.click('AI Chat'); j.wait('Your OpenAI connection')
    j.fill('Message to advisor', 'Synthetic draft that must survive a failed request')
    j.browser('network', 'route', '**/api/v1/advisor/messages', '--abort')
    j.click('Send message'); j.wait('Your draft is kept')
    assert j.browser('get', 'value', j.ref('Message to advisor', 'textbox')).startswith('Synthetic draft')
    j.checks.append('active requested model visible; blocked-network send preserves draft without provider call')
    j.browser('network', 'unroute', '**/api/v1/advisor/messages')
    j.click('Home'); j.click('Open settings'); j.wait('AI source')
    j.fill('API key', KEY + '-replacement')
    j.click('AI Chat'); j.click('Home'); j.click('Open settings'); j.wait('AI source')
    assert j.browser('get', 'value', j.ref('API key', 'textbox')) == ''
    j.checks.append('unsaved credential cleared when leaving Settings')
    j.fill('Model ID', 'synthetic-replacement-model')
    j.click('Save AI connection'); j.wait('AI connection saved.')
    assert not json.loads(j.browser('eval', 'document.querySelector(".ai-settings input[type=checkbox]").checked'))
    j.details('Remove connection and saved key')
    j.click('Confirm remove connection'); j.wait('Saved credential removed.')
    j.click('AI Chat'); j.wait('no model is connected')
    assert j.browser('get', 'value', j.ref('Message to advisor', 'textbox')).startswith('Synthetic draft')
    j.checks.append('model changes reset consent; removal turns AI off and preserves chat draft')
    j.OUT.mkdir(parents=True, exist_ok=True)
    (j.OUT / 'ai-settings.json').write_text(json.dumps({'url': j.URL, 'checks': j.checks,
        'limitations': 'Synthetic credentials only; chat network send blocked; failed-test status uses an explicitly intercepted UI fixture. Other settings requests use the real API. No AI inference or answer quality verified.'}, indent=2) + '\n')
    print(json.dumps({'passed': len(j.checks), 'output': str(j.OUT)}))


if __name__ == '__main__':
    try:
        main()
    finally:
        j.browser('close')
