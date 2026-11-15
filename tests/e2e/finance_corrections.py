"""Real UI CRUD/correction and exact acceptance examples; no API mocks."""
import json
import secrets
import urllib.parse
import journey as j


def main():
    assert urllib.parse.urlparse(j.URL).hostname in {'127.0.0.1', 'localhost', '::1'}
    email, password = 'finance-' + secrets.token_hex(8) + '@example.com', secrets.token_urlsafe(24)
    j.browser('open', j.URL)
    j.click('New account'); j.fill('Display name', 'Finance QA'); j.fill('Email address', email); j.fill('New password', password); j.click('Create account')
    j.wait('Welcome to Barakah.')
    j.click('Accounts'); j.fill('Account name', 'QA cash'); j.fill('Opening balance', '1000.00'); j.click('Add account'); j.wait('QA cash')
    j.click('Transactions'); j.select('Transaction account', 'QA cash (USD)')
    for kind, amount, category, description in [('income', '500.00', 'Salary', 'QA income'), ('expense', '120.00', 'Food', 'QA food')]:
        j.select('Transaction type', kind); j.fill('Transaction amount', amount); j.fill('Category', category); j.fill('Description', description); j.click('Record transaction'); j.wait(description)
    j.check('500 income minus 120 expense produces 380 surplus', '$380.00')
    j.browser('fill', j.ref('Search transaction descriptions'), 'QA food'); j.wait('QA food')
    j.click('Edit transaction'); j.fill('Edit Transaction amount', '275.00'); j.click('Save transaction changes'); j.check('expense edit recalculates ledger', '$1,225.00')
    j.click('Budgets'); j.fill('Budget category', 'Food'); j.fill('Budget limit', '400.00'); j.click('Add budget')
    j.check('400 budget less 275 spent leaves 125', '$125.00')
    j.click('Transactions'); j.click('Edit transaction'); j.fill('Edit Transaction amount', '450.00'); j.click('Save transaction changes'); j.wait('$1,050.00')
    j.click('Budgets'); j.check('450 spent exceeds 400 limit by 50', 'Exceeded by $50.00')
    j.click('Edit budget'); j.fill('Edit Budget limit', '500.00'); j.click('Save budget changes'); j.check('budget edit recalculates remaining', 'Remaining $50.00')
    j.browser('reload'); j.wait('Welcome to Barakah.'); j.click('Budgets'); j.check('budget edit persists after refresh', 'Remaining $50.00')
    j.details('Delete budget'); j.click('Confirm delete budget'); j.check('budget deletion', 'Set a monthly limit')
    j.click('Transactions'); j.browser('fill', j.ref('Search transaction descriptions'), 'QA food'); j.wait('QA food'); j.details('Delete transaction'); j.click('Confirm delete transaction')
    j.check('expense deletion reverses balance', '$1,500.00')
    j.browser('reload'); j.wait('Welcome to Barakah.'); j.click('Transactions'); j.browser('fill', j.ref('Search transaction descriptions'), 'QA food')
    j.check('deleted transaction stays deleted', 'No transactions match these filters')
    j.click('Savings goals'); j.details('Savings & giving goals'); j.fill('Goal name', 'Hajj'); j.fill('Goal target amount', '5000.00'); j.click('Create savings goal'); j.wait('Hajj')
    j.details('Contributions to Hajj'); j.fill('Contribution amount for Hajj', '1250.00'); j.click('Record contribution to Hajj')
    j.check('Hajj progress and remaining are exact', '25.00% complete · Remaining $3,750.00')
    j.details('Contributions to Hajj'); j.details('Correct contribution'); j.fill('Corrected contribution amount', '2500.00'); j.click('Save contribution correction'); j.check('contribution correction updates progress', '50.00% complete')
    j.details('Contributions to Hajj'); j.details('Delete contribution'); j.click('Confirm delete contribution'); j.check('contribution deletion updates progress', '0.00% complete')
    j.click('Edit goal Hajj'); j.fill('Edit Goal name', 'Hajj revised'); j.click('Save goal changes'); j.check('goal edit works with padded database decimals', 'Hajj revised')
    j.browser('reload'); j.wait('Welcome to Barakah.'); j.click('Savings goals'); j.details('Savings & giving goals'); j.check('goal changes persist', 'Hajj revised')
    j.details('Delete goal Hajj revised'); j.click('Confirm delete goal Hajj revised'); j.check('goal deletion', 'Create a savings goal to begin planning.')
    j.click('Sadaqah & giving'); j.details('Record sadaqah given elsewhere'); j.fill('Recorded amount', '50.00'); j.fill('Recipient', 'QA charity'); j.click('Save sadaqah record'); j.details('Sadaqah history'); j.wait('QA charity')
    # Close create form so edit field labels are unique.
    j.details('Record sadaqah given elsewhere'); j.click('Edit sadaqah record'); j.fill('Recorded amount', '75.00'); j.click('Save sadaqah changes'); j.check('sadaqah correction updates annual/monthly totals', '$75.00')
    j.details('Delete sadaqah record'); j.click('Confirm delete sadaqah record'); j.check('sadaqah deletion', 'No sadaqah')
    j.click('Zakat calculator'); j.fill('Cash and bank balances', '15000.00'); j.fill('Manual nisab threshold', '5000.00'); j.fill('Price or threshold source', 'Fictional manual threshold')
    j.fill('Asset and liability treatment notes', 'Eligible cash only; personal jewelry excluded; no deductible debt.')
    j.browser('check', j.ref('I attest that the required lunar-year holding period', 'checkbox'))
    j.click('Save and calculate zakat'); j.check('15000 eligible wealth at 2.5 percent is 375', '$375.00'); j.click('Save calculation to history'); j.wait('Calculation snapshot saved.')
    j.details('Record a zakat payment'); j.fill('Recorded amount', '100.00'); j.fill('Recipient', 'QA zakat recipient')
    import re
    options = j.browser('get', 'html', j.ref('Link calculation (optional)', 'combobox'))
    ids = re.findall(r'<option value="([^"]+)"', options); assert ids
    j.browser('select', j.ref('Link calculation (optional)', 'combobox'), ids[0]); j.click('Save zakat payment record')
    j.details('Record a zakat payment'); j.details('Zakat payment history'); j.click('Edit zakat payment'); j.fill('Recorded amount', '150.00'); j.click('Save zakat payment changes')
    j.details('Calculation history'); j.check('zakat payment correction updates outstanding', 'Remaining $225.00')
    j.check('asset treatment notes persist in calculation snapshot', 'Asset treatment: Eligible cash only')
    j.details('Delete zakat payment record'); j.click('Confirm delete zakat payment'); j.check('zakat payment deletion restores outstanding', 'Remaining $375.00')
    j.browser('reload'); j.wait('Welcome to Barakah.'); j.click('Zakat calculator'); j.details('Calculation history'); j.check('zakat history persists after refresh', 'Remaining $375.00')
    j.screenshot('finance-corrections.png')
    assert not j.browser('errors').strip()
    j.checks.append('no uncaught browser exceptions')
    print(json.dumps({'passed': len(j.checks), 'failed': 0, 'checks': j.checks}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        j.screenshot('finance-corrections-failure.png')
        print(j.browser('snapshot', '-i'))
        raise
    finally:
        j.browser('close')
