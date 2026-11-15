from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import pytest

B = '/api/v1'


def transaction(client, auth, account_id, amount='20.00', kind='expense', **kwargs):
    return client.post(B + '/transactions', headers=auth, json={'account_id': account_id, 'amount': amount, 'kind': kind, 'category': 'food', 'description': 'Lunch', 'occurred_on': '2026-01-15', **kwargs})


def balance(client, auth, account_id):
    return Decimal(next(a['balance'] for a in client.get(B + '/accounts', headers=auth).json() if a['id'] == account_id))


def test_transaction_budget_dashboard_and_reversal(client, auth, account):
    a = account('100.00')
    expense = transaction(client, auth, a['id']).json()
    assert balance(client, auth, a['id']) == 80
    income = transaction(client, auth, a['id'], '50.00', 'income').json()
    assert balance(client, auth, a['id']) == 130
    budget = client.post(B + '/budgets', headers=auth, json={'category': 'food', 'currency': 'USD', 'amount': '100.00', 'month': '2026-01'}).json()
    assert budget['spent'] == '20.00' and budget['remaining'] == '80.00' and budget['utilization_percent'] == '20.00'
    assert client.post(B + '/budgets', headers=auth, json={'category': 'food', 'currency': 'USD', 'amount': '100.00', 'month': '2026-01'}).status_code == 409
    result = client.get(B + '/dashboard?month=2026-01', headers=auth).json()['by_currency'][0]
    assert result['income'] == '50.00' and result['expenses'] == '20.00' and result['savings'] == '30.00'
    assert result['net_worth'] == '130.00'
    assert client.patch(B + '/transactions/' + expense['id'], headers=auth, json={'account_id': a['id'], 'amount': '30.00', 'kind': 'expense', 'category': 'food', 'occurred_on': '2026-01-15'}).status_code == 200
    assert balance(client, auth, a['id']) == 120
    assert client.delete(B + '/transactions/' + expense['id'], headers=auth).status_code == 204
    assert balance(client, auth, a['id']) == 150
    assert client.delete(B + '/transactions/' + income['id'], headers=auth).status_code == 204
    assert balance(client, auth, a['id']) == 100
    assert client.patch(B + '/budgets/' + budget['id'], headers=auth, json={'category': 'food', 'currency': 'USD', 'amount': '200.00', 'month': '2026-01'}).json()['remaining'] == '200.00'


@pytest.mark.parametrize('amount', ['0', '-1', 'NaN', 'Infinity', '0.001', '1000000000.00'])
def test_invalid_amounts(client, auth, account, amount):
    a = account()
    assert transaction(client, auth, a['id'], amount).status_code == 422
    assert balance(client, auth, a['id']) == 100


def test_overdraft_edit_delete_preserve_state(client, auth, account):
    a = account('0.00')
    income = transaction(client, auth, a['id'], '50.00', 'income').json()
    assert transaction(client, auth, a['id'], '60.00').status_code == 409
    assert transaction(client, auth, a['id'], '40.00').status_code == 201
    assert client.delete(B + '/transactions/' + income['id'], headers=auth).status_code == 409
    assert balance(client, auth, a['id']) == 10
    assert client.delete(B + '/accounts/' + a['id'], headers=auth).status_code == 409


def test_transfer_atomic_currency_and_ownership(client, auth, account, register):
    a, b, eur = account(), account('0.00'), account('0.00', 'EUR')
    def transfer(target, amount='30.00'):
        return client.post(B + '/transfers', headers=auth, json={'from_account_id': a['id'], 'to_account_id': target, 'amount': amount, 'occurred_on': '2026-01-15'})
    assert transfer(eur['id']).status_code == 422
    assert transfer(a['id']).status_code == 422
    assert transfer(b['id'], '101.00').status_code == 409
    assert balance(client, auth, a['id']) == 100 and balance(client, auth, b['id']) == 0
    assert transfer(b['id']).status_code == 201
    assert balance(client, auth, a['id']) == 70 and balance(client, auth, b['id']) == 30
    summary = client.get(B + '/dashboard?month=2026-01', headers=auth).json()['by_currency']
    assert len(summary) == 2 and all(v['income'] == '0.00' and v['expenses'] == '0.00' for v in summary)
    tx = client.get(B + '/transactions', headers=auth).json()[0]
    assert client.delete(B + '/transactions/' + tx['id'], headers=auth).status_code == 409
    other, _ = register('other@example.com')
    assert client.get(B + '/accounts', headers=other).json() == []
    assert transaction(client, other, a['id']).status_code == 404
    assert client.get(B + '/transactions?account_id=' + a['id'], headers=other).status_code == 404
    assert client.patch(B + '/accounts/' + a['id'], headers=other, json={'name': 'stolen'}).status_code == 404


def test_filters_pagination_and_exact_decimal(client, auth, account):
    a = account('999999999.99')
    for _ in range(10):
        assert transaction(client, auth, a['id'], '0.01').status_code == 201
    assert balance(client, auth, a['id']) == Decimal('999999999.89')
    assert len(client.get(B + '/transactions?limit=3&offset=2&query=Lunch&category=food&start_date=2026-01-01&end_date=2026-01-31', headers=auth).json()) == 3
    assert client.get(B + '/transactions?query=%25', headers=auth).json() == []
    assert client.get(B + '/transactions?start_date=2026-02-01', headers=auth).json() == []
    assert client.get(B + '/transactions?limit=101', headers=auth).status_code == 422
    assert client.get(B + '/transactions?start_date=2026-03-01&end_date=2026-01-01', headers=auth).status_code == 422


def test_concurrent_overdraft_serialized(client, auth, account):
    a = account('100.00')
    with ThreadPoolExecutor(max_workers=2) as executor:
        codes = list(executor.map(lambda _: transaction(client, auth, a['id'], '80.00').status_code, range(2)))
    assert sorted(codes) == [201, 409]
    assert balance(client, auth, a['id']) == 20


def test_account_type_update_and_empty_delete(client, auth, account):
    a = account()
    assert client.patch(B + '/accounts/' + a['id'], headers=auth, json={'account_type': 'savings'}).json()['account_type'] == 'savings'
    assert client.get(B + '/accounts/' + a['id'], headers=auth).json()['name'] == 'Cash'
    assert client.delete(B + '/accounts/' + a['id'], headers=auth).status_code == 204
    assert client.get(B + '/accounts/' + a['id'], headers=auth).status_code == 404
