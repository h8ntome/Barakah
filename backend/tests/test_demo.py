from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select, func
from app.models import User, Account, Transaction
from app.security import hasher


def demo(client):
    response = client.post('/api/v1/auth/demo')
    assert response.status_code == 201, response.text
    session = response.json()
    return {'Authorization': 'Bearer ' + session['access_token']}, session['user']


def test_demo_isolated_seed_reset_expiry(client, db_setup, register):
    real_headers, real = register()
    a, user_a = demo(client)
    b, user_b = demo(client)
    assert user_a['id'] != user_b['id']
    assert user_a['is_demo'] and not user_a['is_admin']
    accounts = client.get('/api/v1/accounts', headers=a).json()
    assert sorted(Decimal(x['balance']) for x in accounts) == [Decimal('3000.00'), Decimal('12000.00')]
    assert client.patch('/api/v1/accounts/' + accounts[0]['id'], headers=b, json={'name': 'Intruder'}).status_code == 404
    assert client.get('/api/v1/zakat/estimate', headers=a).json()['estimated_due'] == '375.00'
    assert client.get('/api/v1/portfolio', headers=a).json()['by_currency'][0]['cost_basis'] == '8500.00'
    assert Decimal(client.get('/api/v1/goals', headers=a).json()[0]['saved_amount']) == Decimal('1250.00')
    assert client.post('/api/v1/auth/demo/reset', headers=real_headers).status_code == 403
    reset = client.post('/api/v1/auth/demo/reset', headers=a)
    assert reset.status_code == 200, reset.text
    assert reset.json()['user']['id'] != user_a['id']
    assert client.get('/api/v1/auth/me', headers=a).status_code == 401
    assert client.get('/api/v1/auth/me', headers=b).status_code == 200
    with db_setup() as db:
        assert db.get(User, real['user']['id']) is not None
        assert db.get(User, user_a['id']) is None
        assert db.scalar(select(func.count()).select_from(Account).where(Account.user_id == user_a['id'])) == 0
        user = db.get(User, user_b['id'])
        assert user.password_hash.startswith('$argon2id$')
        user.demo_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert client.get('/api/v1/auth/me', headers=b).status_code == 401
    demo(client)
    with db_setup() as db:
        assert db.get(User, user_b['id']) is None


def test_duplicate_and_validation_errors(client, register):
    register()
    response = client.post('/api/v1/auth/register', json={'email': 'ONE@example.com', 'password': 'correct horse battery', 'display_name': 'Another'})
    assert response.status_code == 409
    assert 'already registered' in response.json()['error']['message']
    response = client.post('/api/v1/auth/register', json={'email': 'bad', 'password': 'short', 'display_name': 'Test'})
    assert response.status_code == 422
    assert 'email' in response.text and 'password' in response.text
    assert 'secret-short' not in response.text


def test_demo_seed_failure_rolls_back(client, db_setup, monkeypatch):
    from app import demo as module
    def fail(*args, **kwargs):
        raise ValueError('Injected seed failure')
    monkeypatch.setattr(module.giving, 'create_goal', fail)
    import pytest
    with pytest.raises(ValueError, match='Injected'):
        client.post('/api/v1/auth/demo')
    with db_setup() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0
        assert db.scalar(select(func.count()).select_from(Transaction)) == 0
