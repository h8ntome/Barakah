"""Application regression fixtures, NOT a model benchmark or a model-quality score.

The four original-benchmark regressions are intentional debugging fixtures selected
AFTER that evaluation. They must never be presented as a fresh held-out comparison.
"""
from decimal import Decimal
import pytest

BASE = '/api/v1'


@pytest.mark.parametrize('income,expenses,expected_expenses,expected_savings', [
    ('4250.00', ['1400.00', '480.00', '210.00', '760.00'], '2850.00', '1400.00'),
    ('2000.00', ['1125.75', '389.40', '157.85', '126.20'], '1799.20', '200.80'),
    ('5120.80', ['1775.45', '628.90', '351.25', '920.60'], '3676.20', '1444.60'),
    ('0.30', ['0.10', '0.20'], '0.30', '0.00'),
])
def test_recorded_cashflow_uses_exact_money(client, auth, account, income, expenses,
                                          expected_expenses, expected_savings):
    cash = account('0.00')
    entries = [('income', income), *(('expense', value) for value in expenses)]
    for kind, amount in entries:
        response = client.post(BASE + '/transactions', headers=auth, json={
            'account_id': cash['id'], 'kind': kind, 'amount': amount,
            'category': 'Essentials', 'occurred_on': '2026-11-01',
        })
        assert response.status_code == 201, response.text
    response = client.get(BASE + '/dashboard?month=2026-11', headers=auth)
    assert response.status_code == 200
    totals = response.json()['by_currency'][0]
    assert totals['expenses'] == expected_expenses
    assert totals['savings'] == expected_savings
    assert totals['balance'] == expected_savings
    budget = client.post(BASE + '/budgets', headers=auth, json={
        'category': 'Essentials', 'currency': 'USD', 'month': '2026-11',
        'amount': expected_expenses,
    })
    assert budget.status_code == 201, budget.text
    assert budget.json()['remaining'] == '0.00'
    assert budget.json()['utilization_percent'] == '100.00'


def test_no_income_does_not_invent_savings_rate(client, auth, account):
    cash = account('100.00')
    response = client.post(BASE + '/transactions', headers=auth, json={
        'account_id': cash['id'], 'kind': 'expense', 'amount': '25.00',
        'category': 'Food', 'occurred_on': '2026-11-01',
    })
    assert response.status_code == 201
    totals = client.get(BASE + '/dashboard?month=2026-11', headers=auth).json()['by_currency'][0]
    assert totals['savings'] == '-25.00'
    assert totals['savings_rate_percent'] is None
    assert totals['balance'] == '75.00'


def test_zakat_benchmark_regression_with_explicit_assumptions(client, auth, zakat_profile):
    zakat_profile['assets']['cash'] = '123456.72'
    zakat_profile['haul_complete'] = True
    zakat_profile['manual_nisab'] = '5000.00'
    response = client.put(BASE + '/zakat/profile', headers=auth, json=zakat_profile)
    assert response.status_code == 200, response.text
    result = client.get(BASE + '/zakat/estimate', headers=auth).json()
    assert result['estimated_due'] == '3086.42'
    assert result['eligible'] is True
    assert 'not a ruling' in result['methodology']
    assert Decimal(result['eligible_base']) == Decimal('123456.72')
    # Eligibility is a declared assumption, not inferred by a language model.
    zakat_profile['haul_complete'] = False
    assert client.put(BASE + '/zakat/profile', headers=auth, json=zakat_profile).status_code == 200
    assert client.get(BASE + '/zakat/estimate', headers=auth).json()['estimated_due'] == '0.00'
