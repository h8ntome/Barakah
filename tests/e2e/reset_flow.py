"""Browser reset flow against a local API with a private development outbox.
BARAKAH_RESET_OUTBOX=/path/to/backend/outbox python3 tests/e2e/reset_flow.py
"""
import json
import os
from pathlib import Path
import secrets
import urllib.parse
import urllib.request
import journey as ui


def main():
    if urllib.parse.urlparse(ui.URL).hostname not in {'127.0.0.1', 'localhost', '::1'}:
        raise SystemExit('Local browser testing only')
    email = 'reset-' + secrets.token_hex(6) + '@example.com'
    old_password, new_password = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    api_base = os.environ.get('BARAKAH_API_URL', 'http://127.0.0.1:8000/api/v1')
    if urllib.parse.urlparse(api_base).hostname not in {'127.0.0.1', 'localhost', '::1'}:
        raise SystemExit('Local API only')
    def api(path, payload, method='POST', token=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        with urllib.request.urlopen(urllib.request.Request(api_base + path, data=json.dumps(payload).encode(), headers=headers, method=method), timeout=15) as response:
            body = response.read()
            return json.loads(body) if body else None
    api('/auth/register', {'email': email, 'password': old_password, 'display_name': 'Fictional reset tester'})
    ui.browser('open', ui.URL)
    ui.click('Forgot password?')
    ui.fill('Email address', email)
    ui.click('Request reset')
    ui.check('reset request remains generic', 'If the address is registered')
    outbox = Path(os.environ.get('BARAKAH_RESET_OUTBOX', 'backend/outbox'))
    matches = [(path, json.loads(path.read_text())) for path in outbox.glob('*.json')]
    path, message = next((path, message) for path, message in matches if message['email'] == email)
    ui.browser('open', ui.URL.rstrip('/') + '/reset-password#token=' + urllib.parse.quote(message['token']))
    ui.wait('Choose a new password')
    assert 'token' not in ui.browser('get', 'url')
    assert ui.browser('get', 'value', ui.ref('Password reset token', 'textbox')) == message['token']
    ui.checks.append('fragment token consumed once and removed from URL')
    ui.fill('New password', new_password)
    ui.click('Reset password')
    ui.check('password reset form succeeds', 'Password reset. Sign in with your new password.')
    ui.screenshot('07-reset-confirmed.png')
    ui.fill('Email address', email)
    ui.fill('Password', new_password)
    ui.click('Sign in')
    ui.check('new password signs in', 'Welcome to Barakah.')
    token = api('/auth/login', {'email': email, 'password': new_password})['access_token']
    api('/auth/me', {'password': new_password}, method='DELETE', token=token)
    path.unlink()  # Private notification no longer needed after this isolated test.
    print(json.dumps({'passed': len(ui.checks), 'failed': 0, 'checks': ui.checks}, indent=2))


if __name__ == '__main__':
    try:
        main()
    finally:
        ui.browser('close')
