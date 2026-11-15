import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import jwt
import pytest
from sqlalchemy import select
from app import models as m
from app.config import Settings, get_settings
from app.security import digest, hasher

BASE = '/api/v1'


def csrf(client):
    return {'Origin': 'http://localhost:5173', 'X-CSRF-Token': client.cookies.get('csrf_token')}


def test_register_me_profile_mass_assignment(client, register):
    auth, envelope = register()
    assert envelope['token_type'] == 'bearer'
    assert 'password_hash' not in envelope['user']
    assert client.get(BASE + '/auth/me', headers=auth).json()['email'] == 'one@example.com'
    assert client.patch(BASE + '/auth/profile', headers=auth, json={'is_admin': True}).status_code == 422
    assert client.patch(BASE + '/auth/profile', headers=auth, json={'timezone': 'Not/AZone'}).status_code == 422
    response = client.patch(BASE + '/auth/profile', headers=auth, json={'display_name': 'Changed', 'country': 'PK', 'timezone': 'Asia/Karachi', 'language': 'ur', 'currency': 'PKR'})
    assert response.json()['country'] == 'PK'
    assert response.json()['display_name'] == 'Changed'
    assert response.headers['cache-control'] == 'no-store'


def test_password_is_argon2_and_token_hashes_only(client, auth, db_setup):
    with db_setup() as db:
        user = db.scalar(select(m.User))
        assert user.password_hash.startswith('$argon2id$')
        assert hasher.verify(user.password_hash, 'correct horse battery')
        session = db.scalar(select(m.Session))
        assert session.token_hash == digest(client.cookies['refresh_token'])
        assert session.token_hash != client.cookies['refresh_token']


def test_login_generic_failure_and_duplicate(client, register):
    register()
    for email in ['one@example.com', 'missing@example.com']:
        result = client.post(BASE + '/auth/login', json={'email': email, 'password': 'wrong'})
        assert result.status_code == 401
        assert result.json()['error']['message'] == 'Invalid email or password'
    assert client.post(BASE + '/auth/register', json={'email': 'ONE@example.com', 'password': 'correct horse battery', 'display_name': 'Another'}).status_code == 409
    assert client.post(BASE + '/auth/login', json={'email': 'ONE@example.com', 'password': 'correct horse battery'}).status_code == 200


@pytest.mark.parametrize('payload', [{'email': 'bad', 'password': 'short', 'display_name': 'a'}, {'email': 'new@example.com', 'password': 'correct horse battery', 'display_name': '  '}, {'email': 'new@example.com', 'password': 'correct horse battery', 'display_name': 'a', 'is_admin': True}])
def test_registration_validation_does_not_echo_credentials(client, payload):
    response = client.post(BASE + '/auth/register', json=payload)
    assert response.status_code == 422
    assert payload['password'] not in response.text


def test_cookie_csrf_rotation_and_logout(client, auth):
    old_refresh = client.cookies['refresh_token']
    old_csrf = client.cookies['csrf_token']
    assert client.post(BASE + '/auth/refresh').status_code == 403
    assert client.post(BASE + '/auth/refresh', headers={'Origin': 'http://localhost:5173', 'X-CSRF-Token': 'wrong'}).status_code == 403
    assert client.post(BASE + '/auth/refresh', headers={'Origin': 'https://evil.test', 'X-CSRF-Token': old_csrf}).status_code == 403
    response = client.post(BASE + '/auth/refresh', headers=csrf(client))
    assert response.status_code == 200
    assert client.cookies['refresh_token'] != old_refresh
    assert any('HttpOnly' in value and 'refresh_token=' in value for value in response.headers.get_list('set-cookie'))
    assert client.get(BASE + '/auth/me', headers=auth).status_code == 401
    fresh_auth = {'Authorization': 'Bearer ' + response.json()['access_token']}
    fresh_refresh, fresh_csrf = client.cookies['refresh_token'], client.cookies['csrf_token']
    client.cookies.clear()
    client.cookies.set('refresh_token', old_refresh)
    client.cookies.set('csrf_token', old_csrf)
    assert client.post(BASE + '/auth/refresh', headers=csrf(client)).status_code == 401
    client.cookies.clear()
    client.cookies.set('refresh_token', fresh_refresh)
    client.cookies.set('csrf_token', fresh_csrf)
    assert client.post(BASE + '/auth/logout', headers=csrf(client)).status_code == 204
    assert client.get(BASE + '/auth/me', headers=fresh_auth).status_code == 401


def test_access_tampering_and_expiration(client, register):
    auth, data = register()
    token = data['access_token']
    assert client.get(BASE + '/auth/me', headers={'Authorization': 'Bearer ' + token + 'x'}).status_code == 401
    payload = jwt.decode(token, get_settings().secret_key, algorithms=['HS256'], audience='barakah')
    payload['exp'] = datetime.now(timezone.utc) - timedelta(seconds=1)
    expired = jwt.encode(payload, get_settings().secret_key, algorithm='HS256')
    assert client.get(BASE + '/auth/me', headers={'Authorization': 'Bearer ' + expired}).status_code == 401
    assert client.get(BASE + '/auth/me').status_code == 401


def test_password_change_revokes_all_sessions(client, auth):
    second = client.post(BASE + '/auth/login', json={'email': 'one@example.com', 'password': 'correct horse battery'}).json()
    assert client.post(BASE + '/auth/password', headers=auth, json={'current_password': 'incorrect', 'new_password': 'new secure password'}).status_code == 401
    assert client.post(BASE + '/auth/password', headers=auth, json={'current_password': 'correct horse battery', 'new_password': 'new secure password'}).status_code == 204
    assert client.get(BASE + '/auth/me', headers=auth).status_code == 401
    assert client.get(BASE + '/auth/me', headers={'Authorization': 'Bearer ' + second['access_token']}).status_code == 401
    assert client.post(BASE + '/auth/login', json={'email': 'one@example.com', 'password': 'new secure password'}).status_code == 200


def test_reset_generic_one_use_expiration(client, auth, db_setup):
    existing = client.post(BASE + '/auth/reset/request', json={'email': 'one@example.com'})
    absent = client.post(BASE + '/auth/reset/request', json={'email': 'absent@example.com'})
    assert existing.json() == absent.json()
    files = list(Path(get_settings().reset_outbox).glob('*.json'))
    assert len(files) == 1
    assert files[0].stat().st_mode & 0o077 == 0
    token = json.loads(files[0].read_text())['token']
    assert token not in existing.text
    payload = {'token': token, 'new_password': 'replacement password'}
    assert client.post(BASE + '/auth/reset/confirm', json=payload).status_code == 204
    assert client.post(BASE + '/auth/reset/confirm', json=payload).status_code == 400
    assert client.get(BASE + '/auth/me', headers=auth).status_code == 401
    client.post(BASE + '/auth/reset/request', json={'email': 'one@example.com'})
    files2 = [f for f in Path(get_settings().reset_outbox).glob('*.json') if f != files[0]]
    with db_setup.begin() as db:
        for reset in db.scalars(select(m.PasswordReset)):
            reset.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    payload['token'] = json.loads(files2[0].read_text())['token']
    assert client.post(BASE + '/auth/reset/confirm', json=payload).status_code == 400


def test_rate_limit(client, monkeypatch):
    monkeypatch.setattr(get_settings(), 'auth_rate_limit', 2)
    for _ in range(2):
        assert client.post(BASE + '/auth/login', json={'email': 'missing@example.com', 'password': 'no'}).status_code == 401
    assert client.post(BASE + '/auth/login', json={'email': 'missing@example.com', 'password': 'no'}).status_code == 429


def test_delete_cascades_and_password_required(client, auth, account, db_setup, historical_conversation):
    account()
    historical_conversation()
    assert client.request('DELETE', BASE + '/auth/me', headers=auth, json={'password': 'wrong'}).status_code == 401
    assert client.request('DELETE', BASE + '/auth/me', headers=auth, json={'password': 'correct horse battery'}).status_code == 204
    with db_setup() as db:
        for model in (m.User, m.Session, m.Account, m.Conversation, m.Message):
            assert db.scalar(select(model)) is None
    assert client.get(BASE + '/auth/me', headers=auth).status_code == 401


@pytest.mark.parametrize('settings', [{'environment': 'production'}, {'environment': 'production', 'cookie_secure': True, 'secret_key': 'a' * 40, 'allowed_origins': 'http://localhost:5173'}, {'allowed_origins': '*'}, {'ai_mode': 'mock'}, {'ai_mode': 'local'}])
def test_insecure_configuration_rejected(settings):
    with pytest.raises(ValueError):
        Settings(_env_file=None, **settings)


def test_concurrent_refresh_single_winner(client, auth):
    from concurrent.futures import ThreadPoolExecutor
    from fastapi.testclient import TestClient
    from app.main import app
    refresh, token = client.cookies['refresh_token'], client.cookies['csrf_token']
    def attempt(_):
        with TestClient(app) as isolated:
            isolated.cookies.set('refresh_token', refresh)
            isolated.cookies.set('csrf_token', token)
            return isolated.post(BASE + '/auth/refresh', headers={'Origin': 'http://localhost:5173', 'X-CSRF-Token': token}).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        codes = list(executor.map(attempt, range(2)))
    assert sorted(codes) == [200, 401]
