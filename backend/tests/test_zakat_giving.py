from decimal import Decimal
import pytest
from sqlalchemy import select
from app import models as m
B = '/api/v1'


@pytest.mark.parametrize('cash,debt,haul,expected', [('10000.00','0.00',True,'250.00'),('4999.99','0.00',True,'0.00'),('5000.00','0.00',True,'125.00'),('10000.00','0.00',False,'0.00'),('100.00','200.00',True,'0.00'),('10000.20','0.00',True,'250.01')])
def test_zakat_nisab_haul_debt_round_once(client, auth, zakat_profile, cash, debt, haul, expected):
    zakat_profile['assets']['cash'] = cash
    zakat_profile['assets']['liabilities'] = debt
    zakat_profile['haul_complete'] = haul
    assert client.put(B + '/zakat/profile', headers=auth, json=zakat_profile).status_code == 200
    result = client.get(B + '/zakat/estimate', headers=auth).json()
    assert result['estimated_due'] == expected
    assert Decimal(result['eligible_base']) >= 0


@pytest.mark.parametrize('method,price,nisab', [('gold','75.123456','6385.493760'),('silver','1.00','595.00')])
def test_zakat_manual_metal_provenance(client, auth, zakat_profile, method, price, nisab):
    zakat_profile['nisab_method'] = method
    zakat_profile['manual_nisab'] = None
    assert client.put(B + '/zakat/profile', headers=auth, json=zakat_profile).status_code == 422
    zakat_profile[method + '_price_per_gram'] = price
    assert client.put(B + '/zakat/profile', headers=auth, json=zakat_profile).status_code == 200
    result = client.get(B + '/zakat/estimate', headers=auth).json()
    assert Decimal(result['nisab']) == Decimal(nisab)
    assert result['price_source'] == 'Manual test valuation'
    zakat_profile['haul_start'] = '2027-01-01'
    assert client.put(B + '/zakat/profile', headers=auth, json=zakat_profile).status_code == 422


def test_history_immutable_remaining_currency_ownership(client, auth, zakat_profile, register):
    assert client.get(B + '/zakat/profile', headers=auth).status_code == 404
    client.put(B + '/zakat/profile', headers=auth, json=zakat_profile)
    history = client.post(B + '/zakat/history', headers=auth).json()
    zakat_profile['assets']['cash'] = '20000.00'
    client.put(B + '/zakat/profile', headers=auth, json=zakat_profile)
    assert client.get(B + '/zakat/history', headers=auth).json()[0]['estimate']['estimated_due'] == '250.00'
    payment = {'history_id': history['id'], 'amount': '100.00', 'currency': 'EUR', 'paid_on': '2026-01-16', 'recipient': 'Recipient'}
    assert client.post(B + '/zakat/payments', headers=auth, json=payment).status_code == 422
    payment['currency'] = 'USD'
    assert client.post(B + '/zakat/payments', headers=auth, json=payment).json()['payment_processed'] is False
    assert client.get(B + '/zakat/history', headers=auth).json()[0]['remaining_amount'] == '150.00'
    other, _ = register('other@example.com')
    assert client.post(B + '/zakat/payments', headers=other, json=payment).status_code == 404
    assert client.get(B + '/zakat/history', headers=other).json() == []


def test_sadaqah_filters_summary_edit_delete_goals(client, auth, register):
    data = {'amount': '10.00', 'currency': 'USD', 'paid_on': '2026-01-01', 'recipient': 'Food bank', 'category': 'food'}
    gift = client.post(B + '/sadaqah', headers=auth, json=data).json()
    assert client.get(B + '/sadaqah?category=education', headers=auth).json() == []
    assert client.get(B + '/sadaqah?start_date=2026-02-01', headers=auth).json() == []
    summary = client.get(B + '/sadaqah/summary?category=food', headers=auth).json()[0]
    assert summary['currency'] == 'USD' and summary['total'] == '10.00'
    assert summary['donation_count'] == 1 and summary['by_category'] == {'food': '10.00'}
    data['amount'] = '12.00'
    assert client.patch(B + '/sadaqah/' + gift['id'], headers=auth, json=data).status_code == 200
    goal = client.post(B + '/goals', headers=auth, json={'name': 'Giving target', 'currency': 'USD', 'target_amount': '100.00'}).json()
    assert client.post(B + '/goals/' + goal['id'] + '/contributions', headers=auth, json={'amount': '25.00'}).status_code == 201
    assert Decimal(client.get(B + '/goals', headers=auth).json()[0]['saved_amount']) == 25
    other, _ = register('other@example.com')
    assert client.delete(B + '/sadaqah/' + gift['id'], headers=other).status_code == 404
    assert client.post(B + '/goals/' + goal['id'] + '/contributions', headers=other, json={'amount': '1.00'}).status_code == 404
    assert client.delete(B + '/sadaqah/' + gift['id'], headers=auth).status_code == 204
    assert client.delete(B + '/goals/' + goal['id'], headers=auth).status_code == 204


def test_approved_causes_manual_intentions_admin_only(client, auth, db_setup):
    data = {'title': 'Example food cause', 'category': 'Relief', 'description': 'Manual entry', 'currency': 'USD'}
    assert client.get(B + '/causes', headers=auth).json() == []
    assert client.post(B + '/admin/causes', headers=auth, json=data).status_code == 403
    with db_setup.begin() as db:
        db.scalar(select(m.User)).is_admin = True
    cause = client.post(B + '/admin/causes', headers=auth, json=data).json()
    assert len(client.get(B + '/causes?query=FOOD&category=Relief', headers=auth).json()) == 1
    assert client.post(B + '/donation-intents', headers=auth, json={'cause_id': cause['id'], 'amount': '10.00', 'currency': 'EUR'}).status_code == 422
    result = client.post(B + '/donation-intents', headers=auth, json={'cause_id': cause['id'], 'amount': '10.00', 'currency': 'USD'}).json()
    assert result['status'] == 'recorded' and result['payment_processed'] is False


def test_goal_update_rejects_silent_currency_conversion(client, auth):
    data = {'name': 'Target', 'currency': 'USD', 'target_amount': '100.00'}
    goal = client.post(B + '/goals', headers=auth, json=data).json()
    client.post(B + '/goals/' + goal['id'] + '/contributions', headers=auth, json={'amount': '10.00'})
    data['currency'] = 'EUR'
    assert client.patch(B + '/goals/' + goal['id'], headers=auth, json=data).status_code == 409
    data.update({'currency': 'USD', 'name': 'Updated'})
    assert client.patch(B + '/goals/' + goal['id'], headers=auth, json=data).json()['name'] == 'Updated'
