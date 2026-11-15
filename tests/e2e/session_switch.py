"""Real two-tab shared-cookie regression: never replay A's draft into B's account."""
import json
import os
from pathlib import Path
import secrets
from urllib.parse import urlparse
import journey as j


def main():
    if urlparse(j.URL).hostname not in {'127.0.0.1', 'localhost', '::1'}:
        raise SystemExit('Loopback test only')
    draft = 'Private account draft ' + secrets.token_hex(6)
    os.environ['AGENT_BROWSER_INIT_SCRIPTS'] = str(Path(__file__).with_name('observe_session.js').resolve())
    j.browser('open', j.URL); j.click('Try Demo'); j.wait('Private demo')
    j.click('Accounts'); j.fill('Account name', draft); j.fill('Opening balance', '10.00')
    j.browser('eval', 'window.__mutationChecks = []')
    j.browser('tab', 'new', '--label', 'second', j.URL)
    j.wait('Welcome to Barakah.'); j.click('Settings'); j.click('Sign out')
    j.wait('Welcome back.'); j.click('Try Demo'); j.wait('Private demo')
    j.browser('tab', 't1'); j.click('Add account')
    j.wait('Welcome to Barakah.'); j.click('Accounts')
    j.browser('wait', '--load', 'networkidle')
    assert draft not in j.browser('get', 'text', 'body'), 'A private draft was copied into B'
    assert json.loads(j.browser('eval', 'window.__mutationChecks')) == [401], 'Mutation was replayed'
    j.browser('reload'); j.wait('Welcome to Barakah.'); j.click('Accounts')
    assert draft not in j.browser('get', 'text', 'body'), 'Private draft persisted under B'
    assert not j.browser('errors').strip()
    print(json.dumps({'passed': 3, 'failed': 0, 'checks': [
        'revoked A mutation attempted exactly once, HTTP 401',
        'shared-cookie account switch never replays the private draft',
        'B still has no private draft after reload',
    ]}, indent=2))


if __name__ == '__main__':
    try:
        main()
    finally:
        j.browser('close')
