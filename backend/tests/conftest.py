import os
from pathlib import Path
os.environ['ENVIRONMENT'] = 'test'
os.environ['AUTH_RATE_LIMIT'] = '1000'
from alembic import command
from alembic.config import Config
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.engine import make_url
from uuid import uuid4
from app import db as database
from app.config import get_settings
from app.main import app
from app.security import limiter


@pytest.fixture
def db_setup(tmp_path, monkeypatch):
    settings = get_settings()
    url = f'sqlite:///{tmp_path / "test.db"}'
    admin_engine = None
    schema = None
    if os.environ.get('TEST_DATABASE_URL'):
        admin_engine = database.make_engine(os.environ['TEST_DATABASE_URL'])
        schema = 'barakah_test_' + uuid4().hex
        with admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA {schema}'))
        url = make_url(os.environ['TEST_DATABASE_URL']).update_query_dict({'options': f'-csearch_path={schema}'}).render_as_string(hide_password=False)
    monkeypatch.setattr(settings, 'database_url', url)
    monkeypatch.setattr(settings, 'reset_outbox', str(tmp_path / 'outbox'))
    monkeypatch.setattr(settings, 'ai_mode', 'mock')
    monkeypatch.setattr(settings, 'auth_rate_limit', 1000)
    monkeypatch.setattr(settings, 'advisor_rate_limit', 30)
    limiter.entries.clear()
    config = Config(str(Path(__file__).parents[1] / 'alembic.ini'))
    command.upgrade(config, 'head')
    engine = database.make_engine(url)
    factory = sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(database, 'SessionLocal', factory)
    yield factory
    engine.dispose()
    if admin_engine is not None:
        with admin_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA {schema} CASCADE'))
        admin_engine.dispose()


@pytest.fixture
def client(db_setup):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def register(client):
    def create(email='one@example.com'):
        response = client.post('/api/v1/auth/register', json={'email': email, 'password': 'correct horse battery', 'display_name': 'Test User'})
        assert response.status_code == 201, response.text
        data = response.json()
        return {'Authorization': 'Bearer ' + data['access_token']}, data
    return create


@pytest.fixture
def auth(register):
    return register()[0]


@pytest.fixture
def account(client, auth):
    def create(balance='100.00', currency='USD'):
        response = client.post('/api/v1/accounts', headers=auth, json={'name': 'Cash', 'currency': currency, 'opening_balance': balance})
        assert response.status_code == 201, response.text
        return response.json()
    return create


@pytest.fixture
def zakat_profile():
    return {'currency': 'USD', 'assets': {'cash': '10000.00', 'investments': '0.00', 'gold': '0.00', 'silver': '0.00', 'business': '0.00', 'liabilities': '0.00'}, 'nisab_method': 'manual', 'manual_nisab': '5000.00', 'gold_price_per_gram': None, 'silver_price_per_gram': None, 'price_source': 'Manual test valuation', 'valuation_date': '2026-01-15', 'haul_start': '2025-01-01', 'haul_complete': True, 'rate': '0.025'}
