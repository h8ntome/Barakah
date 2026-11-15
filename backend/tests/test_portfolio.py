from decimal import Decimal
import pytest
B = '/api/v1'


def holding(client, auth, **kwargs):
    response = client.post(B + '/portfolio/holdings', headers=auth, json={'symbol': 'TEST', 'name': 'Manual test holding', 'currency': 'USD', **kwargs})
    assert response.status_code == 201, response.text
    return response.json()


def trade(client, auth, holding_id, side, quantity, price, fees='0.00', traded_on='2026-01-01'):
    return client.post(B + '/portfolio/trades', headers=auth, json={'holding_id': holding_id, 'side': side, 'quantity': quantity, 'price': price, 'fees': fees, 'traded_on': traded_on})


def test_weighted_average_buy_sell_fees_quotes(client, auth):
    h = holding(client, auth)
    assert h['screening_status'] == 'unverified'
    assert trade(client, auth, h['id'], 'buy', '10', '10', '1.00').status_code == 201
    assert trade(client, auth, h['id'], 'buy', '10', '20', '1.00').status_code == 201
    p = client.get(B + '/portfolio', headers=auth).json()
    assert Decimal(p['holdings'][0]['cost_basis']) == 302
    assert p['holdings'][0]['average_cost'] == '15.100000'
    assert p['by_currency'][0]['market_value'] is None
    result = trade(client, auth, h['id'], 'sell', '5', '25', '1.00')
    assert Decimal(result.json()['realized_gain']) == Decimal('48.50')
    quote = client.put(B + '/portfolio/holdings/' + h['id'] + '/quote', headers=auth, json={'price': '22', 'as_of': '2026-01-15', 'source': 'Manual statement'}).json()
    assert Decimal(quote['cost_basis']) == Decimal('226.50')
    assert Decimal(quote['market_value']) == 330
    assert Decimal(quote['unrealized_gain']) == Decimal('103.50')
    assert quote['quote_source'] == 'Manual statement'
    assert trade(client, auth, h['id'], 'sell', '15', '20').status_code == 201
    p = client.get(B + '/portfolio', headers=auth).json()['holdings'][0]
    assert Decimal(p['quantity']) == 0 and Decimal(p['cost_basis']) == 0
    assert Decimal(p['realized_gain']) == 122


def test_invalid_sell_order_precision_and_ownership(client, auth, register):
    h = holding(client, auth)
    assert trade(client, auth, h['id'], 'sell', '1', '10').status_code == 409
    assert trade(client, auth, h['id'], 'buy', '0.0000001', '10').status_code == 422
    assert trade(client, auth, h['id'], 'buy', '1.000001', '10.123456').status_code == 201
    assert trade(client, auth, h['id'], 'sell', '0.5', '1', '1.00').status_code == 409
    assert trade(client, auth, h['id'], 'buy', '1', '10', traded_on='2025-12-01').status_code == 422
    other, _ = register('other@example.com')
    assert trade(client, other, h['id'], 'buy', '1', '10').status_code == 404
    assert client.get(B + '/portfolio', headers=other).json()['holdings'] == []
    assert client.put(B + '/portfolio/holdings/' + h['id'] + '/quote', headers=other, json={'price': '10', 'as_of': '2026-01-01', 'source': 'Manual'}).status_code == 404


def test_multiple_portfolios_currencies_and_missing_valuation(client, auth, register):
    first = client.post(B + '/portfolios', headers=auth, json={'name': 'First'}).json()
    second = client.post(B + '/portfolios', headers=auth, json={'name': 'Second'}).json()
    a = holding(client, auth, portfolio_id=first['id'])
    b = holding(client, auth, portfolio_id=second['id'], currency='EUR')
    trade(client, auth, a['id'], 'buy', '1', '10')
    trade(client, auth, b['id'], 'buy', '2', '10')
    assert len(client.get(B + '/portfolio', headers=auth).json()['by_currency']) == 2
    assert len(client.get(B + '/portfolio?portfolio_id=' + first['id'], headers=auth).json()['holdings']) == 1
    assert client.delete(B + '/portfolios/' + first['id'], headers=auth).status_code == 409
    assert client.get(B + '/dashboard', headers=auth).json()['by_currency'][0]['net_worth'] is None
    other, _ = register('other@example.com')
    assert client.post(B + '/portfolio/holdings', headers=other, json={'portfolio_id': first['id'], 'symbol': 'OTHER', 'name': 'No', 'currency': 'USD'}).status_code == 404


def test_screening_missing_inputs_thresholds_provenance(client, auth):
    h = holding(client, auth)
    endpoint = B + '/portfolio/holdings/' + h['id'] + '/screening'
    from datetime import date
    data = {'source': 'Manual annual statement', 'assessed_on': date.today().isoformat(), 'notes': 'Educational only'}
    response = client.put(endpoint, headers=auth, json=data).json()
    assert response['screening_status'] == 'uncertain'
    assert len(response['screening_assessment']['missing_inputs']) == 4
    data.update({'prohibited_business': False, 'debt_to_assets': '0.30', 'interest_income_to_revenue': '0.05', 'interest_assets_to_assets': '0.30'})
    response = client.put(endpoint, headers=auth, json=data).json()
    assert response['screening_status'] == 'compliant_under_selected_methodology'
    assert response['screening_assessment']['methodology_version'] == 'illustrative-configurable-ratios-v1'
    data['debt_to_assets'] = '0.300001'
    assert client.put(endpoint, headers=auth, json=data).json()['screening_status'] == 'non_compliant'
    data['debt_threshold'] = '0.31'
    assert client.put(endpoint, headers=auth, json=data).json()['screening_status'] == 'compliant_under_selected_methodology'
    data['prohibited_business'] = True
    assert client.put(endpoint, headers=auth, json=data).json()['screening_status'] == 'non_compliant'
    assert client.put(endpoint, headers=auth, json={'status': 'compliant', 'source': 'me', 'assessed_on': '2026-01-01', 'notes': 'No inputs'}).status_code == 422
