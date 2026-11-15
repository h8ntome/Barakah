"""Real-browser authentication/demo acceptance. Run against an isolated local DB.
BARAKAH_UI_URL=http://127.0.0.1:8081 BARAKAH_TEST_DB=/tmp/barakah-audit/app.db python3 tests/e2e/auth_demo.py
"""
import json
import os
from pathlib import Path
import secrets
import sqlite3
import urllib.parse
import journey as j

j.OUT = Path(__file__).resolve().parents[2] / 'audit' / 'artifacts'


def main():
    assert urllib.parse.urlparse(j.URL).hostname in {'127.0.0.1', 'localhost', '::1'}
    email = 'audit-' + secrets.token_hex(8) + '@example.com'
    password = secrets.token_urlsafe(24)
    j.browser('open', j.URL)
    j.click('New account')
    j.fill('Display name', 'Audit Judge')
    j.fill('Email address', email)
    j.fill('New password', password)
    j.click('Create account')
    j.check('register reaches authenticated dashboard', 'Welcome to Barakah.')
    if os.environ.get('BARAKAH_TEST_DB'):
        with sqlite3.connect('file:' + os.environ['BARAKAH_TEST_DB'] + '?mode=ro', uri=True) as db:
            rows = db.execute('SELECT password_hash FROM users WHERE email=?', (email,)).fetchall()
            assert len(rows) == 1 and rows[0][0].startswith('$argon2id$')
        j.checks.append('database user exists with Argon2id hash')
    else:
        raise AssertionError('BARAKAH_TEST_DB required for database verification')
    j.click('Settings')
    j.click('Sign out')
    j.check('logout protects dashboard', 'Welcome back.')
    j.click('Investments')
    j.check('protected navigation while logged out', 'Welcome back.')
    j.fill('Email address', email)
    j.fill('Password', 'Incorrect-password-value')
    j.click('Sign in')
    j.check('wrong password reports useful error', 'Invalid email or password')
    j.fill('Password', password)
    j.click('Sign in')
    j.click('Home')
    j.check('new account can log in', 'Welcome to Barakah.')
    j.browser('reload')
    j.check('refresh retains session', 'Welcome to Barakah.')
    j.click('Settings')
    j.click('Sign out')
    j.click('New account')
    j.fill('Display name', 'Duplicate')
    j.fill('Email address', email)
    j.fill('New password', password)
    j.click('Create account')
    j.check('duplicate rejected clearly', 'This email is already registered.')
    j.screenshot('auth-duplicate.png')
    j.click('Try Demo')
    j.check('demo authenticated and labeled', 'Private demo')
    j.check('demo income', '$4,500.00')
    j.check('demo expense', '$2,850.00')
    j.click('Transactions')
    j.select('Transaction account', 'Demo checking (USD)')
    j.select('Transaction type', 'income')
    j.fill('Transaction amount', '500.00')
    j.fill('Category', 'Demo isolation')
    j.fill('Description', 'Only this demo session')
    j.click('Record transaction')
    j.check('demo accepts real persisted writes', 'Only this demo session')
    j.browser('reload')
    j.wait('Welcome to Barakah.')
    j.click('Transactions')
    j.check('demo changes survive refresh', 'Only this demo session')
    j.screenshot('demo-transactions.png')
    original_session = j.SESSION
    j.SESSION = original_session + '-second'
    try:
        j.browser('open', j.URL)
        j.click('Try Demo')
        j.check('independent demo starts from template', '$4,500.00')
        j.click('Transactions')
        assert 'Only this demo session' not in j.browser('get', 'text', 'body')
        j.checks.append('demo writes do not leak to another browser session')
        j.click('Zakat calculator')
        j.check('demo zakat calculation', '$375.00')
    finally:
        j.browser('close')
        j.SESSION = original_session
    j.click('Settings')
    j.click('Reset demo data')
    j.check('reset returns original demo totals', '$4,500.00')
    j.click('Transactions')
    assert 'Only this demo session' not in j.browser('get', 'text', 'body')
    j.checks.append('reset removes only current demo changes')
    j.browser('set', 'viewport', '390', '844')
    j.screenshot('demo-mobile.png')
    assert j.browser('eval', 'document.documentElement.scrollWidth > innerWidth') == 'false'
    j.checks.append('mobile no horizontal overflow')
    assert not j.browser('errors').strip()
    j.checks.append('no uncaught browser exceptions')
    print(json.dumps({'passed': len(j.checks), 'failed': 0, 'checks': j.checks}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        j.screenshot('auth-demo-failure.png')
        print(j.browser('snapshot', '-i'))
        raise
    finally:
        j.browser('close')
