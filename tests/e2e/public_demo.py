"""Explicitly authorized public smoke: synthetic data only, no production mocks.
BARAKAH_PUBLIC_SMOKE=1 python3 tests/e2e/public_demo.py
Creates two expiring demos and deletes only its own temporary registered user.
"""
import json
import os
from pathlib import Path
import secrets
import tempfile
import journey as j

j.URL = 'https://barakah-gamma.vercel.app'
j.OUT = Path(__file__).resolve().parents[2] / 'audit/artifacts/public'


def main():
    if os.environ.get('BARAKAH_PUBLIC_SMOKE') != '1':
        raise SystemExit('Explicit BARAKAH_PUBLIC_SMOKE=1 required for public synthetic writes.')
    j.browser('open', j.URL)
    j.wait('Welcome back.')
    j.click('Try Demo')
    j.check('public Try Demo authenticates', 'Private demo')
    j.check('stored demo income', '$4,500.00')
    j.check('stored demo spending', '$2,850.00')
    j.screenshot('desktop-home.png')
    # The cookies command filters by the current URL and omits /api-scoped cookies.
    with tempfile.TemporaryDirectory(prefix='barakah-public-state-') as private:
        state = Path(private) / 'state.json'
        j.browser('state', 'save', str(state))
        cookies = json.loads(state.read_text())['cookies']
    refresh = next(c for c in cookies if c['name'] == 'refresh_token')
    assert refresh['secure'] and refresh['httpOnly'] and refresh['path'] == '/api/v1/auth'
    j.checks.append('live refresh cookie is Secure and HttpOnly')
    j.click('Transactions')
    j.select('Transaction account', 'Demo checking (USD)')
    j.select('Transaction type', 'income')
    j.fill('Transaction amount', '500.00')
    j.fill('Category', 'Public smoke')
    j.fill('Description', 'Fictional public isolation check')
    j.click('Record transaction')
    j.check('public demo writes stored records', 'Fictional public isolation check')
    j.browser('reload')
    j.wait('Welcome to Barakah.')
    j.click('Transactions')
    j.check('reload refreshes session and retains edits', 'Fictional public isolation check')
    j.browser('fill', j.ref('Search transaction descriptions'), 'Fictional public isolation check')
    j.wait('Fictional public isolation check')
    j.click('Edit transaction')
    j.fill('Edit Transaction amount', '600.00')
    j.click('Save transaction changes')
    j.check('public transaction correction persists', '$600.00')

    first = j.SESSION
    j.SESSION = first + '-second'
    try:
        j.browser('open', j.URL)
        j.wait('Welcome back.')
        j.click('Try Demo')
        j.check('second tester has independent seed totals', '$4,500.00')
        j.click('Transactions')
        j.wait('Fictional salary')
        assert 'Fictional public isolation check' not in j.browser('get', 'text', 'body')
        j.checks.append('first tester edits do not leak to second tester')
        j.select('Transaction account', 'Demo checking (USD)')
        j.select('Transaction type', 'income')
        j.fill('Transaction amount', '25.00')
        j.fill('Category', 'Public smoke')
        j.fill('Description', 'Second tester retained record')
        j.click('Record transaction')
        j.wait('Second tester retained record')
        j.SESSION = first
        j.click('Settings')
        j.click('Reset demo data')
        j.check('reset restores first demo', '$4,500.00')
        j.click('Transactions')
        j.wait('Fictional salary')
        assert 'Fictional public isolation check' not in j.browser('get', 'text', 'body')
        j.checks.append('reset removes first demo edits')
        j.SESSION = first + '-second'
        j.browser('reload')
        j.wait('Welcome to Barakah.')
        j.click('Transactions')
        j.check('reset does not delete another tester records', 'Second tester retained record')
        assert not j.browser('errors').strip()
    finally:
        j.SESSION = first + '-second'
        j.browser('close')
        j.SESSION = first

    j.click('Zakat calculator')
    j.check('public zakat calculation', '$375.00')
    j.click('AI financial guide')
    j.fill('Message to advisor', 'Fictional availability check')
    j.click('Send message')
    j.check('AI is unavailable without saving fake advice', 'No message was saved.')
    j.click('Home')
    j.browser('set', 'viewport', '390', '844')
    j.screenshot('mobile-transactions.png')
    assert j.browser('eval', 'document.documentElement.scrollWidth > innerWidth') == 'false'
    j.checks.append('public mobile layout has no horizontal overflow')
    j.click('Settings')
    j.click('Sign out')
    j.check('demo logout removes authenticated UI', 'Welcome back.')

    email, password = 'public-smoke-' + secrets.token_hex(8) + '@example.com', secrets.token_urlsafe(24)
    j.click('New account')
    j.fill('Display name', 'Fictional Public QA')
    j.fill('Email address', email)
    j.fill('New password', password)
    j.click('Create account')
    j.check('public registration succeeds', 'Welcome to Barakah.')
    j.click('Settings')
    j.click('Sign out')
    j.wait('Welcome back.')
    j.fill('Email address', email)
    j.fill('Password', password)
    j.click('Sign in')
    j.check('newly registered user can log in', 'Welcome to Barakah.')
    j.browser('reload')
    j.check('registered session survives reload', 'Welcome to Barakah.')
    j.click('Settings')
    j.details('Delete account and personal data')
    j.fill('Password to confirm deletion', password)
    j.browser('check', j.ref('I understand that all my records will be deleted.', 'checkbox'))
    j.click('Permanently delete account')
    j.check('only temporary QA account is deleted', 'Welcome back.')
    assert not j.browser('errors').strip()
    j.checks.append('no uncaught browser exceptions')
    print(json.dumps({'url': j.URL, 'passed': len(j.checks), 'failed': 0, 'checks': j.checks}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        j.screenshot('failure.png')
        raise
    finally:
        j.browser('close')
