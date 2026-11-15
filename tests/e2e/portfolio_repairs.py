"""Real Chromium portfolio repair journey against a local built app/backend.

BARAKAH_UI_URL=http://127.0.0.1:8876 python3 tests/e2e/portfolio_repairs.py
Requires agent-browser; creates a fictional user. Screenshots go to a temporary directory.
"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
from urllib.parse import urlparse

URL = os.environ.get('BARAKAH_UI_URL', 'http://127.0.0.1:8876')
SESSION = 'portfolio-repairs-' + secrets.token_hex(4)
OUT = Path(tempfile.mkdtemp(prefix='barakah-portfolio-screens-'))


def browser(*args):
    result = subprocess.run(['agent-browser', '--session', SESSION, *args], capture_output=True, text=True, timeout=35)
    if result.returncode:
        raise AssertionError(f'{args}: {result.stdout} {result.stderr}')
    return result.stdout.strip()


def ref(name, role):
    refs = json.loads(browser('snapshot', '-i', '--json'))['data']['refs']
    matches = [key for key, item in refs.items() if (item['name'] == name or item['name'].startswith(name + ' ')) and item['role'] == role]
    exact = [key for key in matches if refs[key]['name'] == name]
    matches = exact or matches
    assert len(matches) == 1, (name, matches, refs)
    return '@' + matches[0]


def click(name):
    browser('click', ref(name, 'button'))


def fill(name, value):
    browser('fill', ref(name, 'textbox'), value)


def details(name):
    browser('eval', f"Array.from(document.querySelectorAll('summary')).find(x => x.textContent === {json.dumps(name)})?.scrollIntoView({{block:'center'}})")
    browser('find', 'text', name, 'click', '--exact')


def wait(text):
    browser('wait', '--text', text)


def main():
    assert urlparse(URL).hostname in {'127.0.0.1', 'localhost', '::1'}, 'Local test hosts only'
    browser('open', URL)
    click('New account')
    fill('Display name', 'Portfolio Reviewer')
    fill('Email address', f'portfolio-{secrets.token_hex(6)}@example.com')
    fill('New password', secrets.token_urlsafe(24))
    click('Create account')
    wait('Welcome to Barakah.')
    click('Investments')
    details('Create or manage portfolios')
    fill('Portfolio name', 'Repair portfolio')
    click('Create portfolio')
    wait('Repair portfolio')
    details('Add a holding')
    browser('select', ref('Holding portfolio', 'combobox'), 'Repair portfolio')
    fill('Holding symbol', 'REPAIR')
    fill('Holding name', 'Tracked repair holding')
    click('Create holding')
    wait('REPAIR · Tracked repair holding')
    details('Record a buy or sell')
    browser('select', ref('Trade holding', 'combobox'), 'REPAIR (USD)')
    fill('Quantity', '10')
    fill('Trade price per unit', '50')
    click('Record trade')
    wait('Cost $500')
    details('Trade history')
    details('Correct latest trade')
    browser('select', ref('Corrected trade side', 'combobox'), 'sell')
    fill('Corrected quantity', '12')
    click('Save trade correction')
    wait('Cannot sell more than the held quantity')
    assert browser('get', 'value', ref('Corrected quantity', 'textbox')) == '12'
    browser('select', ref('Corrected trade side', 'combobox'), 'buy')
    click('Save trade correction')
    wait('12.000000 units')
    wait('Cost $600')
    details('Remove latest tracked trade')
    browser('check', ref('I confirm removal of this tracked trade.', 'checkbox'))
    click('Confirm remove tracked trade')
    wait('Cost $0')
    wait('No trades recorded.')
    fill('Quantity', '12')
    fill('Trade price per unit', '50')
    click('Record trade')
    wait('Cost $600')
    details('Edit holding details for REPAIR')
    fill('Updated holding name', 'Corrected holding name')
    click('Save holding details')
    wait('REPAIR · Corrected holding name')
    details('Update manual valuation for REPAIR')
    fill('Quoted price per unit', '0')
    fill('Quote source', 'Manual zero valuation')
    click('Save manual valuation')
    wait('Value: $0')
    details('Update manual valuation for REPAIR')
    assert browser('get', 'value', ref('Quoted price per unit', 'textbox')) in {'0', '0.000000'}
    details('Update manual valuation for REPAIR')
    details('Screen REPAIR')
    fill('Screening evidence source', 'Manual evidence')
    click('Evaluate screening')
    wait('Screening: uncertain')
    browser('select', ref('View portfolio', 'combobox'), 'Repair portfolio')
    wait('REPAIR · Corrected holding name')
    details('Delete tracked holding REPAIR')
    wait('trade and screening records')
    click('Confirm delete tracked holding')
    wait('REPAIR · Corrected holding name')
    checkbox = ref('I confirm removal of this tracked holding and all its trade and screening records.', 'checkbox')
    assert json.loads(browser('eval', "Array.from(document.querySelectorAll('form')).find(form => form.textContent.includes('Confirm delete tracked holding')).querySelector('input[type=checkbox]').required")) is True
    for width in (1280, 320):
        browser('set', 'viewport', str(width), '900')
        browser('eval', "Array.from(document.querySelectorAll('summary')).find(x => x.textContent === 'Delete tracked holding REPAIR').scrollIntoView({block:'center'})")
        assert json.loads(browser('eval', 'document.documentElement.scrollWidth <= window.innerWidth')) is True
        browser('screenshot', str(OUT / f'delete-confirmation-{width}.png'))
    browser('check', checkbox)
    click('Confirm delete tracked holding')
    wait('No holdings yet.')
    wait('No trades recorded.')
    print('PASS: correction 10×50→12×50, oversell rollback/draft retention, latest-trade removal, metadata edit, zero quote, screening, portfolio selection and confirmed cascade deletion; 320/1280px no overflow')
    print(f'Screenshots: {OUT}')


if __name__ == '__main__':
    try:
        main()
    finally:
        browser('close')
