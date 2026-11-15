"""Deployment boundary checks; PostgreSQL variant exercises the actual ASGI export."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy.pool import NullPool
from app.config import Settings
from app.db import make_engine

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('prefix', ['postgres://', 'postgresql://', 'postgresql+psycopg://'])
def test_hosted_database_url_uses_installed_driver(prefix):
    suffix = 'user:encoded%40password@pool.example/db?sslmode=require'
    settings = Settings(_env_file=None, database_url=prefix + suffix)
    assert settings.database_url == 'postgresql+psycopg://' + suffix
    assert Settings(_env_file=None, database_url='sqlite:///test.db').database_url == 'sqlite:///test.db'


def test_serverless_uses_hosted_pooler(monkeypatch):
    monkeypatch.setenv('VERCEL', '1')
    engine = make_engine('postgresql+psycopg://localhost/example')
    assert isinstance(engine.pool, NullPool)
    assert engine.hide_parameters
    engine.dispose()


def run_entrypoint(code, database_url, **overrides):
    env = {**os.environ, 'VERCEL': '1', 'DATABASE_URL': database_url,
           'SECRET_KEY': 'test-only-secret-not-for-any-deployment-123456',
           'ALLOWED_ORIGINS': 'https://demo.example', 'RESET_OUTBOX': '',
           'FRONTEND_DIST': '', 'SMTP_HOST': '', **overrides}
    return subprocess.run([sys.executable, '-c', code], cwd=ROOT, env=env,
                          text=True, capture_output=True, timeout=30)


@pytest.mark.parametrize('url', ['', 'sqlite:////tmp/not-durable.db'])
def test_entrypoint_rejects_missing_or_ephemeral_database(url):
    result = run_entrypoint('from api.index import app', url)
    assert result.returncode != 0
    assert 'persistent PostgreSQL' in result.stderr


def test_entrypoint_forces_secure_configuration():
    result = run_entrypoint('''
from api.index import app
from app.config import get_settings
from fastapi.testclient import TestClient
settings = get_settings()
assert settings.environment == 'production'
assert settings.cookie_secure
assert settings.ai_mode == 'unavailable'
with TestClient(app, base_url='https://demo.example') as client:
    assert client.get('/health').status_code == 200
    denied = client.post('/api/v1/auth/demo', headers={'Origin': 'https://attacker.example'})
    assert denied.status_code == 403
    assert denied.json()['error']['code'] == 'origin_forbidden'
''', 'postgresql://localhost/not-connected', ENVIRONMENT='development', COOKIE_SECURE='false', AI_MODE='mock')
    assert result.returncode == 0, result.stderr
    result = run_entrypoint('from api.index import app', 'postgresql://localhost/not-connected', SECRET_KEY='')
    assert result.returncode != 0
    assert 'Production requires' in result.stderr


def test_vercel_routes_api_before_spa():
    config = json.loads((ROOT / 'vercel.json').read_text())
    assert config['rewrites'][0] == {'source': '/api/:path*', 'destination': '/api/index.py'}
    assert config['rewrites'][-1]['destination'] == '/index.html'
    assert config['framework'] is None
    assert 'VITE_API_BASE_URL=/api/v1' in config['buildCommand']
    assert (ROOT / '.python-version').read_text().strip() == '3.13'
    # Vercel's dependency scanner cannot resolve nested -r includes at build time.
    assert (ROOT / 'requirements.txt').read_text() == (ROOT / 'backend/requirements.txt').read_text()


@pytest.mark.skipif(not os.environ.get('TEST_DATABASE_URL'), reason='Requires isolated PostgreSQL test schema')
def test_real_postgres_demo_through_vercel_entrypoint(db_setup):
    url = db_setup.kw['bind'].url.render_as_string(hide_password=False)
    result = run_entrypoint('''
from api.index import app
from fastapi.testclient import TestClient
origin = {'Origin': 'https://demo.example'}
with TestClient(app, base_url='https://demo.example') as first, TestClient(app, base_url='https://demo.example') as second:
    assert first.get('/api/v1/health').status_code == 200
    response = first.post('/api/v1/auth/demo', headers=origin)
    assert response.status_code == 201, response.text
    original = response.json()
    assert original['user']['is_demo'] and not original['user']['is_admin']
    cookies = response.headers.get_list('set-cookie')
    assert all('Secure' in cookie for cookie in cookies)
    assert any('HttpOnly' in cookie and 'refresh_token=' in cookie for cookie in cookies)
    other = second.post('/api/v1/auth/demo', headers=origin).json()
    assert other['user']['id'] != original['user']['id']
    headers = {**origin, 'Authorization': 'Bearer ' + original['access_token']}
    assert first.get('/api/v1/dashboard', headers=headers).status_code == 200
    added = first.post('/api/v1/accounts', headers=headers, json={'name': 'Remote persistent record', 'currency': 'USD', 'opening_balance': '123.45'})
    assert added.status_code == 201, added.text
    refreshed = first.post('/api/v1/auth/refresh', headers={**origin, 'X-CSRF-Token': first.cookies.get('csrf_token')})
    assert refreshed.status_code == 200, refreshed.text
    headers['Authorization'] = 'Bearer ' + refreshed.json()['access_token']
    assert added.json()['id'] in [row['id'] for row in first.get('/api/v1/accounts', headers=headers).json()]
    other_headers = {'Authorization': 'Bearer ' + other['access_token']}
    assert added.json()['id'] not in [row['id'] for row in second.get('/api/v1/accounts', headers=other_headers).json()]
    reset = first.post('/api/v1/auth/demo/reset', headers=headers)
    assert reset.status_code == 200, reset.text
    assert reset.json()['user']['id'] != original['user']['id']
    assert second.get('/api/v1/dashboard', headers=other_headers).status_code == 200
''', url)
    assert result.returncode == 0, result.stderr
