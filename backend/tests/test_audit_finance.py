from decimal import Decimal
from datetime import date

BASE = '/api/v1'


def test_required_cashflow_budget_and_dashboard(client, auth, account):
    cash = account('1000')
    today = date.today().isoformat()
    def tx(kind, amount, category):
        body = {'account_id': cash['id'], 'kind': kind, 'amount': amount, 'category': category, 'occurred_on': today}
        response = client.post(BASE + '/transactions', headers=auth, json=body)
        assert response.status_code == 201
        return body, response.json()['id']
    income, income_id = tx('income', '500.00', 'Salary')
    expense, expense_id = tx('expense', '120.00', 'Food')
    def summary():
        response = client.get(BASE + '/dashboard', headers=auth)
        assert response.status_code == 200, response.text
        return response.json()
    assert summary()['by_currency'][0]['savings'] == '380.00'
    assert len(summary()['recent_transactions']) == 2
    budget = client.post(BASE + '/budgets', headers=auth, json={'category': 'Food', 'currency': 'USD', 'month': today[:7], 'amount': '400.00'}).json()
    expense['amount'] = '275.00'
    assert client.patch(BASE + '/transactions/' + expense_id, headers=auth, json=expense).status_code == 200
    assert summary()['budgets'][0]['remaining'] == '125.00'
    expense['amount'] = '450.00'
    assert client.patch(BASE + '/transactions/' + expense_id, headers=auth, json=expense).status_code == 200
    assert summary()['budgets'][0]['exceeded_amount'] == '50.00'
    assert summary()['by_currency'][0]['expense_category_percent'] == {'Food': '100.00'}
    assert client.delete(BASE + '/transactions/' + expense_id, headers=auth).status_code == 204
    assert summary()['by_currency'][0]['savings'] == '500.00'
    assert client.delete(BASE + '/transactions/' + income_id, headers=auth).status_code == 204
    assert summary()['by_currency'][0]['balance'] == '1000.00'


def test_payment_corrections_ownership_currency_and_summary(client, register, zakat_profile):
    a, _ = register()
    b, _ = register('b@example.com')
    zakat_profile['assets']['cash'] = '15000.00'
    assert client.put(BASE + '/zakat/profile', headers=a, json=zakat_profile).status_code == 200
    history = client.post(BASE + '/zakat/history', headers=a).json()
    body = {'amount': '100.00', 'currency': 'USD', 'paid_on': date.today().isoformat(), 'recipient': 'Synthetic', 'history_id': history['id']}
    payment = client.post(BASE + '/zakat/payments', headers=a, json=body).json()
    url = BASE + '/zakat/payments/' + payment['id']
    assert client.patch(url, headers=b, json=body).status_code == 404
    assert client.delete(url, headers=b).status_code == 404
    assert client.patch(url, headers=a, json={**body, 'currency': 'EUR'}).status_code == 422
    assert client.get(BASE + '/zakat/history', headers=a).json()[0]['remaining_amount'] == '275.00'
    assert client.patch(url, headers=a, json={**body, 'amount': '150.00'}).status_code == 200
    summary = client.get(BASE + '/dashboard', headers=a).json()
    assert summary['zakat']['estimated_due'] == '375.00'
    assert summary['latest_zakat_record']['remaining_amount'] == '225.00'
    assert client.delete(url, headers=a).status_code == 204
    assert client.get(BASE + '/zakat/history', headers=a).json()[0]['remaining_amount'] == '375.00'
    sadaqah = client.post(BASE + '/sadaqah', headers=a, json={k: v for k, v in body.items() if k != 'history_id'}).json()
    assert client.delete(BASE + '/zakat/payments/' + sadaqah['id'], headers=a).status_code == 404


def test_goal_progress_and_contribution_correction(client, register):
    a, _ = register()
    b, _ = register('b@example.com')
    goal = client.post(BASE + '/goals', headers=a, json={'name': 'Hajj', 'currency': 'USD', 'target_amount': '5000.00'}).json()
    root = BASE + '/goals/' + goal['id'] + '/contributions'
    item = client.post(root, headers=a, json={'amount': '1250.00'}).json()
    url = root + '/' + item['id']
    view = client.get(BASE + '/goals', headers=a).json()[0]
    assert view['progress_percent'] == '25.00' and view['remaining_amount'] == '3750.00'
    assert client.patch(url, headers=b, json={'amount': '1.00'}).status_code == 404
    assert client.delete(url, headers=b).status_code == 404
    assert client.patch(url, headers=a, json={'amount': '-1.00'}).status_code == 422
    assert client.patch(url, headers=a, json={'amount': '2500.00'}).status_code == 200
    assert client.get(BASE + '/dashboard', headers=a).json()['goals'][0]['progress_percent'] == '50.00'
    assert client.delete(url, headers=a).status_code == 204
    assert Decimal(client.get(BASE + '/goals', headers=a).json()[0]['saved_amount']) == 0
