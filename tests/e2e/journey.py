"""Real Chromium journey against running Barakah frontend + backend.

Requires the installed agent-browser CLI. No network or model responses are mocked.
BARAKAH_UI_URL=http://127.0.0.1:5173 python3 tests/e2e/journey.py
Creates a unique fictional account; never uses production data.
"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
import urllib.parse

URL = os.environ.get('BARAKAH_UI_URL', 'http://127.0.0.1:5173')
SESSION = 'barakah-journey-' + secrets.token_hex(4)
OUT = Path(__file__).resolve().parents[2] / 'docs' / 'testing' / 'screenshots'
checks = []


def browser(*args):
    result = subprocess.run(['agent-browser', '--session', SESSION, *args], capture_output=True, text=True, timeout=35)
    if result.returncode:
        raise AssertionError(f'Browser command {args[0]} failed: {result.stdout} {result.stderr}')
    return result.stdout.strip()


def ref(name, role=None):
    data = json.loads(browser('snapshot', '-i', '--json'))['data']['refs']
    found = [key for key, item in data.items() if (item['name'] == name or item['name'].startswith(name + ' ')) and (role is None or item['role'] == role)]
    exact = [key for key in found if data[key]['name'] == name]
    found = exact or found
    if len(found) != 1:
        raise AssertionError(f'Expected one visible {role} {name!r}, got {len(found)}; snapshot={data}')
    return '@' + found[0]


def click(name):
    browser('click', ref(name, 'button'))


def fill(name, value):
    browser('fill', ref(name, 'textbox'), value)


def select(name, value):
    browser('select', ref(name, 'combobox'), value)


def details(name):
    # Center nested disclosures above the fixed mobile navigation before clicking.
    browser('eval', f"Array.from(document.querySelectorAll('summary')).find(x => x.textContent === {json.dumps(name)})?.scrollIntoView({{block:'center'}})")
    browser('find', 'text', name, 'click', '--exact')


def wait(text):
    browser('wait', '--text', text)


def check(name, text):
    wait(text)
    checks.append(name)
    print('PASS:', name, flush=True)


def screenshot(name):
    OUT.mkdir(parents=True, exist_ok=True)
    browser('screenshot', str(OUT / name))


def main():
    if urllib.parse.urlparse(URL).hostname not in {'localhost', '127.0.0.1', '::1'}:
        raise SystemExit('Refusing to create browser test accounts on a non-loopback host.')
    email = f'journey-{secrets.token_hex(6)}@example.com'
    password = secrets.token_urlsafe(24)
    browser('open', URL)
    click('New account')
    fill('Display name', 'Fictional Judge')
    fill('Email address', email)
    fill('New password', password)
    click('Create account')
    check('registration and protected dashboard', 'Welcome to Barakah.')
    check('empty financial workspace', 'No balances yet.')

    click('Accounts')
    fill('Account name', 'Judge cash')
    fill('Opening balance', '1000.00')
    click('Add account')
    check('account persisted', 'Judge cash')
    click('Transactions')
    select('Transaction account', 'Judge cash (USD)')
    select('Transaction type', 'income')
    fill('Transaction amount', '4000.00')
    fill('Category', 'Salary')
    fill('Description', 'Fictional salary')
    browser('network', 'route', '**/api/v1/transactions', '--abort')
    click('Record transaction')
    check('network error is recoverable', 'Cannot reach Barakah.')
    assert browser('get', 'value', ref('Transaction amount', 'textbox')) == '4000.00'
    checks.append('failed transaction preserves draft')
    browser('network', 'unroute', '**/api/v1/transactions')
    click('Record transaction')
    check('income recorded', 'Fictional salary')
    select('Transaction type', 'expense')
    fill('Transaction amount', '200.00')
    fill('Category', 'Food')
    fill('Description', 'Fictional groceries')
    click('Record transaction')
    check('expense and dashboard updated', '$4,800.00')
    browser('eval', "document.querySelector('.screen-page:not([hidden]) .screen-content').scrollTop = 0")
    screenshot('01-finance.png')
    click('Budgets')
    fill('Budget category', 'Food')
    fill('Budget limit', '500.00')
    click('Add budget')
    check('budget actual spending', '$200.00')
    check('budget remaining', '$300.00')

    click('Zakat calculator')
    fill('Cash and bank balances', '10000.00')
    select('Nisab method', 'gold')
    fill('Gold price per gram', '80.00')
    fill('Price or threshold source', 'Fictional manual test valuation; NOT live')
    browser('check', ref('I attest that the required holding period', 'checkbox'))
    click('Save and calculate zakat')
    check('zakat calculated server-side', '$250.00')
    click('Save calculation to history')
    check('calculation saved', 'Calculation snapshot saved.')
    details('Record a zakat payment')
    fill('Recorded amount', '50.00')
    fill('Recipient', 'Fictional zakat recipient')
    # A single saved snapshot: select its option by value from the rendered select.
    select_ref = ref('Link calculation (optional)', 'combobox')
    options = browser('get', 'html', select_ref)
    import re
    ids = re.findall(r'<option value="([^"]+)"', options)
    assert ids, 'Saved calculation must be selectable'
    browser('select', select_ref, ids[0])
    click('Save zakat payment record')
    details('Calculation history')
    check('partial zakat payment remaining', '$200.00')
    screenshot('02-zakat.png')

    click('Sadaqah & giving')
    details('Record sadaqah given elsewhere')
    fill('Recorded amount', '25.00')
    fill('Recipient', 'Fictional community fund')
    click('Save sadaqah record')
    details('Sadaqah history')
    check('sadaqah persisted without payment processing', 'Fictional community fund')
    details('Charitable goals')
    fill('Goal name', 'Fictional giving goal')
    fill('Goal target amount', '100.00')
    click('Create charitable goal')
    check('charitable goal persisted', 'Fictional giving goal')
    details('Contributions to Fictional giving goal')
    wait('Contribution amount for Fictional giving goal')
    fill('Contribution amount for Fictional giving goal', '20.00')
    click('Record contribution to Fictional giving goal')
    check('goal contribution persisted', '$20.00')

    click('Investments')
    details('Create or manage portfolios')
    fill('Portfolio name', 'Judge portfolio')
    click('Create portfolio')
    check('portfolio created', 'Judge portfolio')
    details('Add a holding')
    select('Holding portfolio', 'Judge portfolio')
    fill('Holding symbol', 'DEMO')
    fill('Holding name', 'Fictional Example')
    click('Create holding')
    check('holding created', 'DEMO')
    details('Record a buy or sell')
    select('Trade holding', 'DEMO (USD)')
    fill('Quantity', '10')
    fill('Trade price per unit', '20.00')
    click('Record trade')
    check('trade cost basis', '$200.00')
    details('Update manual valuation for DEMO')
    fill('Quoted price per unit', '21.00')
    fill('Quote source', 'Fictional manual quote; NOT live')
    click('Save manual valuation')
    check('manual portfolio valuation', '$210.00')
    details('Screen DEMO')
    fill('Screening evidence source', 'No verified fundamentals available')
    fill('Screening notes and limitations', 'Fictional fixture; insufficient information')
    browser('fill', ref('Screening evidence validity days', 'spinbutton'), '30')
    click('Evaluate screening')
    check('missing-data screening stays uncertain', 'uncertain')
    screenshot('03-investments.png')

    click('Home')
    click('Settings')
    browser('check', ref('Allow advisor requests.', 'checkbox'))
    click('Save settings')
    wait('Saved.')
    click('AI financial guide')
    browser('check', ref('Include my monthly income and expense summary', 'checkbox'))
    fill('Message to advisor', 'How can I plan giving?')
    click('Send message')
    check('mock AI response and history', 'Track income and expenses by currency')
    check('opt-in context uses verified totals', 'Verified backend monthly totals')
    screenshot('04-chat.png')
    browser('reload')
    wait('Welcome to Barakah.')
    click('AI financial guide')
    check('conversation persists after reload', 'How can I plan giving?')
    click('Home')
    click('Settings')
    click('Sign out')
    check('logout protects workspace', 'Welcome back.')
    click('Investments')
    check('protected navigation stays signed out', 'Welcome back.')
    fill('Email address', email)
    fill('Password', password)
    click('Sign in')
    click('Home')
    check('login restores stored balance', '$4,800.00')
    check('quoted portfolio updates net worth', '$5,010.00')
    click('Investments')
    details('Screen DEMO')
    assert browser('get', 'value', ref('Screening evidence validity days', 'spinbutton')) == '30'
    checks.append('custom screening validity persists after reload')
    click('Home')
    browser('set', 'viewport', '390', '844')
    screenshot('05-mobile.png')
    overflow = browser('eval', 'document.documentElement.scrollWidth > window.innerWidth')
    assert overflow.strip() == 'false', overflow
    checks.append('mobile has no document overflow')
    errors = browser('errors')
    assert not errors.strip() or 'No' in errors, errors
    print(json.dumps({'passed': len(checks), 'failed': 0, 'checks': checks}, indent=2))


if __name__ == '__main__':
    started = time.monotonic()
    try:
        main()
    except Exception:
        try:
            screenshot('failure.png')
            print(browser('snapshot', '-i'), flush=True)
        except Exception:
            pass
        raise
    finally:
        browser('close')
        print(f'Elapsed: {time.monotonic() - started:.1f}s', flush=True)
