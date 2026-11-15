from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import select

from app import models as m
from test_portfolio import B, holding, trade


def summary(client, auth):
    return client.get(B + '/portfolio', headers=auth).json()


def correction(**kwargs):
    return {'side': 'buy', 'quantity': '12', 'price': '50', 'fees': '0.00', 'traded_on': '2026-01-01', **kwargs}


def history(client, auth, **params):
    response = client.get(B + '/portfolio/trades', headers=auth, params=params)
    assert response.status_code == 200
    return response.json()


def test_latest_purchase_correction_and_removal(client, auth):
    h = holding(client, auth)
    t = trade(client, auth, h['id'], 'buy', '10', '50').json()
    assert Decimal(summary(client, auth)['holdings'][0]['cost_basis']) == 500
    endpoint = B + '/portfolio/trades/' + t['id']
    response = client.patch(endpoint, headers=auth, json=correction())
    assert response.status_code == 200
    result = summary(client, auth)
    assert Decimal(result['holdings'][0]['quantity']) == 12
    assert Decimal(result['holdings'][0]['cost_basis']) == 600
    assert result['by_currency'][0]['total_purchases_including_fees'] == '600.00'
    assert history(client, auth)[0]['can_correct'] is True
    # Repeated corrections must start from the snapshot, not compound previous edits.
    assert client.patch(endpoint, headers=auth, json=correction(quantity='11', fees='1.23')).status_code == 200
    assert Decimal(summary(client, auth)['holdings'][0]['cost_basis']) == Decimal('551.23')
    assert client.delete(endpoint, headers=auth).status_code == 204
    restored = summary(client, auth)['holdings'][0]
    assert all(Decimal(restored[key]) == 0 for key in ('quantity', 'cost_basis', 'realized_gain'))
    assert history(client, auth) == []


def test_same_day_order_and_exact_sell_reversal(client, auth):
    h = holding(client, auth)
    first = trade(client, auth, h['id'], 'buy', '3.000001', '10.123456', '0.01').json()
    before = summary(client, auth)
    second = trade(client, auth, h['id'], 'sell', '1.000001', '15.654321', '0.02').json()
    records = history(client, auth, limit=1)
    assert records[0]['id'] == second['id'] and records[0]['sequence'] == 2
    assert history(client, auth, limit=1, offset=1)[0]['can_correct'] is False
    first_url, second_url = (B + '/portfolio/trades/' + t['id'] for t in (first, second))
    unchanged = summary(client, auth)
    for method in ('patch', 'delete'):
        response = getattr(client, method)(first_url, headers=auth, **({'json': correction()} if method == 'patch' else {}))
        assert response.status_code == 409
        assert response.json()['error']['code'] == 'not_latest_trade'
    assert summary(client, auth) == unchanged
    data = correction(side='sell', quantity='3.000001', price='15.654321', fees='0.02')
    assert client.patch(second_url, headers=auth, json=data).status_code == 200
    sold = summary(client, auth)['holdings'][0]
    assert Decimal(sold['quantity']) == Decimal(sold['cost_basis']) == 0
    assert Decimal(sold['realized_gain']) == Decimal('16.562601')
    assert client.delete(second_url, headers=auth).status_code == 204
    assert summary(client, auth) == before
    assert history(client, auth)[0]['can_correct'] is True


@pytest.mark.parametrize('changes,status', [
    ({'side': 'sell', 'quantity': '11'}, 409),
    ({'side': 'sell', 'quantity': '1', 'price': '1', 'fees': '2'}, 409),
    ({'quantity': '1000000000'}, 409),
    ({'quantity': '0.0000001'}, 422),
    ({'price': 'NaN'}, 422),
    ({'traded_on': '2025-12-31'}, 422),
])
def test_correction_validation_rolls_back_every_record(client, auth, changes, status):
    h = holding(client, auth)
    trade(client, auth, h['id'], 'buy', '10', '50')
    latest = trade(client, auth, h['id'], 'buy', '2', '60').json()
    before, records = summary(client, auth), history(client, auth)
    response = client.patch(B + '/portfolio/trades/' + latest['id'], headers=auth, json=correction(**changes))
    assert response.status_code == status, response.text
    assert summary(client, auth) == before
    assert history(client, auth) == records


def test_holding_metadata_ownership_conflicts_and_symbol_provenance(client, auth, register):
    h = holding(client, auth)
    other, _ = register('other@example.com')
    endpoint = B + '/portfolio/holdings/' + h['id']
    data = {'name': 'Corrected name', 'symbol': 'FIXED'}
    for method in ('patch', 'delete'):
        assert getattr(client, method)(endpoint, headers=other, **({'json': data} if method == 'patch' else {})).status_code == 404
    assert client.patch(endpoint, headers=auth, json=data).status_code == 200
    duplicate = holding(client, auth, symbol='DUP')
    assert client.patch(endpoint, headers=auth, json={**data, 'symbol': duplicate['symbol']}).status_code == 409
    assert {item['symbol'] for item in summary(client, auth)['holdings']} == {'FIXED', 'DUP'}
    trade(client, auth, h['id'], 'buy', '1', '50')
    assert client.patch(endpoint, headers=auth, json={**data, 'symbol': 'WRONG'}).status_code == 409
    assert client.patch(endpoint, headers=auth, json={**data, 'name': 'Updated name'}).status_code == 200
    assert client.patch(endpoint, headers=auth, json={**data, 'currency': 'EUR'}).status_code == 422


@pytest.mark.parametrize('evidence', ['quote', 'screening'])
def test_symbol_cannot_transfer_quote_or_screening_claim(client, auth, evidence):
    h = holding(client, auth)
    url = B + '/portfolio/holdings/' + h['id']
    body = {'source': 'Manual', 'as_of': date.today().isoformat(), 'price': '0'} if evidence == 'quote' else {'source': 'Manual', 'assessed_on': date.today().isoformat()}
    assert client.put(url + '/' + evidence, headers=auth, json=body).status_code == 200
    assert client.patch(url, headers=auth, json={'name': 'Renamed', 'symbol': 'OTHER'}).status_code == 409


def test_trade_ownership_and_portfolio_scoped_history(client, auth, register):
    p = client.post(B + '/portfolios', headers=auth, json={'name': 'First'}).json()
    q = client.post(B + '/portfolios', headers=auth, json={'name': 'Second'}).json()
    a, b = (holding(client, auth, portfolio_id=item['id']) for item in (p, q))
    t = trade(client, auth, a['id'], 'buy', '10', '50').json()
    trade(client, auth, b['id'], 'buy', '2', '20')
    assert [row['id'] for row in history(client, auth, portfolio_id=p['id'])] == [t['id']]
    assert history(client, auth, portfolio_id=p['id'], holding_id=b['id']) == []
    other, _ = register('other@example.com')
    endpoint = B + '/portfolio/trades/' + t['id']
    before = summary(client, auth)
    assert client.patch(endpoint, headers=other, json=correction()).status_code == 404
    assert client.delete(endpoint, headers=other).status_code == 404
    for params in ({'portfolio_id': p['id']}, {'holding_id': a['id']}):
        assert client.get(B + '/portfolio/trades', headers=other, params=params).status_code == 404
    assert summary(client, auth) == before


def test_holding_delete_cascades_only_its_records_and_never_moves_cash(client, auth, account, db_setup):
    account(balance='1000.00')
    h, keep = holding(client, auth), holding(client, auth, symbol='KEEP')
    for item in (h, keep):
        trade(client, auth, item['id'], 'buy', '10', '50')
        assert client.put(B + '/portfolio/holdings/' + item['id'] + '/screening', headers=auth, json={'source': 'Manual', 'assessed_on': date.today().isoformat()}).status_code == 200
    cash = client.get(B + '/accounts', headers=auth).json()
    assert client.delete(B + '/portfolio/holdings/' + h['id'], headers=auth).status_code == 204
    assert client.get(B + '/accounts', headers=auth).json() == cash
    assert [item['id'] for item in summary(client, auth)['holdings']] == [keep['id']]
    with db_setup() as db:
        assert db.get(m.Holding, h['id']) is None
        assert [t.holding_id for t in db.scalars(select(m.Trade))] == [keep['id']]
        assert [r.holding_id for r in db.scalars(select(m.ScreeningRecord))] == [keep['id']]
        assert db.get(m.Portfolio, keep['portfolio_id']) is not None


def test_zero_quote_and_future_screening_rejection(client, auth):
    h = holding(client, auth)
    trade(client, auth, h['id'], 'buy', '10', '50')
    url = B + '/portfolio/holdings/' + h['id']
    assert client.put(url + '/quote', headers=auth, json={'price': '0.000000', 'as_of': date.today().isoformat(), 'source': 'Worthless'}).status_code == 200
    result = summary(client, auth)
    assert result['by_currency'][0]['market_value'] == '0.00'
    assert result['by_currency'][0]['unrealized_gain'] == '-500.00'
    assert result['by_currency'][0]['valuation_complete'] is True
    assert result['holdings'][0]['unrealized_return_percent'] == '-100.00'
    assert client.put(url + '/screening', headers=auth, json={'source': 'Future', 'assessed_on': (date.today() + timedelta(days=1)).isoformat()}).status_code == 422
    assert client.get(url + '/screenings', headers=auth).json() == []


@pytest.mark.parametrize('snapshot,age,stale', [
    ({'max_age_days': 90}, 90, False), ({'max_age_days': 90}, 91, True),
    ({'max_age_days': None}, 0, True), ({'max_age_days': '90'}, 0, True),
    ({'max_age_days': False}, 0, True), ({'max_age_days': -1}, 0, True),
    ({'max_age_days': 4000}, 0, True), ([], 0, True), (None, 0, True),
    ({}, -1, True), ({}, None, True),
])
def test_defensive_legacy_screening_age(client, auth, db_setup, snapshot, age, stale):
    h = holding(client, auth)
    with db_setup() as db:
        item = db.get(m.Holding, h['id'])
        item.screening_assessment = snapshot
        item.screening_date = date.today() - timedelta(days=age) if age is not None else None
        item.screening_status = 'compliant_under_selected_methodology'
        db.commit()
    result = summary(client, auth)['holdings'][0]
    assert result['needs_reevaluation'] is stale
    assert result['screening_status'] == ('uncertain' if stale else 'compliant_under_selected_methodology')


def test_additive_migration_preserves_legacy_and_new_trade_reversal(client, auth):
    h = holding(client, auth)
    legacy = [trade(client, auth, h['id'], 'buy', '10', '50').json(), trade(client, auth, h['id'], 'sell', '3', '60', '0.01').json()]
    before = summary(client, auth)
    config = Config(str(Path(__file__).parents[1] / 'alembic.ini'))
    command.downgrade(config, 'b17d8e0a1f42')
    command.upgrade(config, 'head')
    assert summary(client, auth) == before
    records = history(client, auth)
    assert [item['id'] for item in records] == sorted(item['id'] for item in legacy)
    assert all(item['sequence'] is None and item['correction_unavailable_reason'] == 'legacy_trade' for item in records)
    for item in records:
        endpoint = B + '/portfolio/trades/' + item['id']
        assert client.patch(endpoint, headers=auth, json=correction()).status_code == 409
        assert client.delete(endpoint, headers=auth).status_code == 409
    new = trade(client, auth, h['id'], 'sell', '2', '60').json()
    assert new['sequence'] == 1 and new['can_correct'] is True
    endpoint = B + '/portfolio/trades/' + new['id']
    assert client.patch(endpoint, headers=auth, json=correction(side='sell', quantity='1', price='70')).status_code == 200
    assert client.delete(endpoint, headers=auth).status_code == 204
    assert summary(client, auth) == before
    assert history(client, auth) == records


def test_side_correction_recalculates_loss_without_compounding(client, auth):
    h = holding(client, auth)
    trade(client, auth, h['id'], 'buy', '10', '50', '1.00')
    t = trade(client, auth, h['id'], 'buy', '2', '60').json()
    endpoint = B + '/portfolio/trades/' + t['id']
    assert client.patch(endpoint, headers=auth, json=correction(side='sell', quantity='2', price='40', fees='1.00')).status_code == 200
    result = summary(client, auth)['holdings'][0]
    assert Decimal(result['quantity']) == 8
    assert Decimal(result['cost_basis']) == Decimal('400.8')
    assert Decimal(result['realized_gain']) == Decimal('-21.2')
    assert client.patch(endpoint, headers=auth, json=correction(quantity='2', price='60')).status_code == 200
    result = summary(client, auth)['holdings'][0]
    assert Decimal(result['quantity']) == 12
    assert Decimal(result['cost_basis']) == 621
    assert Decimal(result['realized_gain']) == 0


def test_concurrent_oversells_leave_one_trade_and_exact_balance(client, auth):
    from concurrent.futures import ThreadPoolExecutor
    h = holding(client, auth)
    trade(client, auth, h['id'], 'buy', '10', '50')
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: trade(client, auth, h['id'], 'sell', '7', '60'), range(2)))
    assert sorted(response.status_code for response in responses) == [201, 409]
    result = summary(client, auth)['holdings'][0]
    assert Decimal(result['quantity']) == 3
    assert Decimal(result['cost_basis']) == 150
    assert Decimal(result['realized_gain']) == 70
    records = history(client, auth)
    assert len(records) == 2 and records[0]['sequence'] == 2
    assert client.delete(B + '/portfolio/trades/' + records[0]['id'], headers=auth).status_code == 204
    assert Decimal(summary(client, auth)['holdings'][0]['cost_basis']) == 500
