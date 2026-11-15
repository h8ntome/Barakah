from datetime import date, timedelta
from app.calculations import zakat_estimate


def test_new_user_timestamps_are_utc_and_update(client, auth):
    before = client.get('/api/v1/auth/me', headers=auth).json()
    assert before['created_at'].endswith('+00:00')
    after = client.patch('/api/v1/auth/profile', headers=auth, json={'display_name': 'Changed'}).json()
    assert after['created_at'] == before['created_at']
    assert after['updated_at'] >= before['updated_at']


def test_giving_periods_frequency_distribution_and_ownership(client, auth, register):
    today = date.today()
    data = {'currency': 'USD', 'recipient': 'Food bank', 'category': 'food', 'amount': '10.00', 'paid_on': today.isoformat()}
    assert client.post('/api/v1/sadaqah', headers=auth, json=data).status_code == 201
    other, _ = register('other-giver@example.com')
    client.post('/api/v1/sadaqah', headers=other, json=data)
    client.post('/api/v1/sadaqah', headers=auth, json={**data, 'amount': '5.00', 'paid_on': date(today.year - 1, 1, 1).isoformat()})
    summary = client.get('/api/v1/sadaqah/summary', headers=auth).json()[0]
    assert summary == {'currency': 'USD', 'total': '15.00', 'monthly_total': '10.00', 'annual_total': '10.00', 'donation_count': 2, 'by_recipient': {'Food bank': '15.00'}, 'by_category': {'food': '15.00'}}


def test_configurable_nisab_and_all_asset_categories(zakat_profile):
    zakat_profile.update(nisab_method='gold', gold_price_per_gram='100', gold_nisab_grams='87.48')
    zakat_profile['assets'].update(cash='0', savings='5000', other='3748')
    result = zakat_estimate(zakat_profile)
    assert result['nisab'] == '8748.00'
    assert result['eligible'] is True
    assert result['estimated_due'] == '218.70'


def test_screening_history_staleness_and_ownership(client, auth, register):
    h = client.post('/api/v1/portfolio/holdings', headers=auth, json={'symbol': 'DEMO', 'name': 'Fictional fixture', 'currency': 'USD'}).json()
    url = '/api/v1/portfolio/holdings/' + h['id']
    data = {'source': 'Manual fictional fixture', 'assessed_on': (date.today() - timedelta(days=91)).isoformat(), 'prohibited_business': False, 'debt_to_assets': '0.1', 'interest_income_to_revenue': '0.01', 'interest_assets_to_assets': '0.1'}
    response = client.put(url + '/screening', headers=auth, json=data).json()
    assert response['needs_reevaluation'] is True
    assert response['screening_status'] == 'uncertain'
    assert response['screening_assessment']['status'] == 'compliant_under_selected_methodology'
    data['assessed_on'] = date.today().isoformat()
    response = client.put(url + '/screening', headers=auth, json=data).json()
    assert response['needs_reevaluation'] is False
    history = client.get(url + '/screenings', headers=auth).json()
    assert len(history) == 2
    assert all(record['assessment']['methodology_version'] for record in history)
    other, _ = register('second-screen@example.com')
    assert client.get(url + '/screenings', headers=other).status_code == 404


def test_dashboard_categories_rate_and_transaction_order(client, auth, account):
    a = account()
    for kind, amount, day in [('income', '1000', '2026-01-01'), ('expense', '200', '2026-01-02')]:
        assert client.post('/api/v1/transactions', headers=auth, json={'account_id': a['id'], 'kind': kind, 'amount': amount, 'category': 'Food', 'occurred_on': day}).status_code == 201
    data = client.get('/api/v1/dashboard?month=2026-01', headers=auth).json()['by_currency'][0]
    assert data['expense_categories'] == {'Food': '200.00'}
    assert data['savings_rate_percent'] == '80.00'
    descending = client.get('/api/v1/transactions', headers=auth).json()
    ascending = client.get('/api/v1/transactions?sort=date_asc', headers=auth).json()
    assert descending[0]['occurred_on'] == '2026-01-02'
    assert ascending[0]['occurred_on'] == '2026-01-01'


def test_portfolio_allocation_and_total_purchases(client, auth):
    holding = client.post('/api/v1/portfolio/holdings', headers=auth, json={'symbol': 'DEMO', 'name': 'Fixture', 'currency': 'USD'}).json()
    client.post('/api/v1/portfolio/trades', headers=auth, json={'holding_id': holding['id'], 'side': 'buy', 'quantity': '10', 'price': '20', 'fees': '1', 'traded_on': date.today().isoformat()})
    client.put('/api/v1/portfolio/holdings/' + holding['id'] + '/quote', headers=auth, json={'price': '22', 'as_of': date.today().isoformat(), 'source': 'Manual fixture'})
    summary = client.get('/api/v1/portfolio', headers=auth).json()
    assert summary['holdings'][0]['allocation_percent'] == '100.00'
    assert summary['by_currency'][0]['total_purchases_including_fees'] == '201.00'
