"""Synthetic credentials and mocked provider responses; no real API success is claimed."""
import base64
import json
from datetime import timedelta
import pytest
from pydantic import SecretStr
from sqlalchemy import select, func
from app import ai_connections as c, ai_limits, external_ai, models as m
from app.config import get_settings
from app.security import limiter
from test_ai_http import provider

B = '/api/v1'
KEY = 'synthetic-test-credential-' + 'x' * 24


def csrf(client, auth):
    return {**auth, 'Origin': 'http://localhost:5173', 'X-CSRF-Token': client.cookies.get('csrf_token', '')}


def settings(client, auth):
    return client.get(B + '/ai/connection', headers=auth).json()


def save(client, auth, **overrides):
    body = dict(mode='external', provider='openai', model_id='test-model', api_key=KEY,
                expected_revision=settings(client, auth)['revision'])
    body.update(overrides)
    return client.put(B + '/ai/connection', headers=csrf(client, auth), json=body)


def consent(client, auth):
    assert client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': True}).status_code == 200


def chat(client, auth, **extra):
    return client.post(B + '/advisor/messages', headers=auth, json={
        'text': 'A synthetic question', 'connection_revision': settings(client, auth)['revision'], **extra})


@pytest.fixture
def external(monkeypatch, client):
    config = get_settings()
    monkeypatch.setattr(config, 'user_ai_enabled', True)
    monkeypatch.setattr(config, 'ai_credential_key', SecretStr(base64.urlsafe_b64encode(b't' * 32).decode()))
    monkeypatch.setattr(config, 'ai_allowed_base_urls', 'https://provider.example/v1')
    monkeypatch.setattr(config, 'ai_requests_per_minute', 60)
    calls = []
    state = {'status': 200, 'hook': None, 'exception': None, 'body': {
        'model': 'test-model-snapshot', 'choices': [{'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': 'Synthetic protocol fixture, not real AI.'}}],
        'usage': {'prompt_tokens': 30, 'completion_tokens': 12}}}
    async def exchange(base, credential, payload):
        calls.append((base, credential, payload))
        if state['hook']:
            state['hook']()
        if state['exception']:
            raise state['exception']
        return state['status'], state['body']
    monkeypatch.setattr(external_ai, 'exchange', exchange)
    return calls, state


@pytest.mark.parametrize('successful', [True, False])
def test_inherited_local_test_persists_status_without_changing_consent_or_destination(client, auth, provider, db_setup, successful):
    calls, state = provider
    consent(client, auth)
    before = settings(client, auth)
    assert before['mode'] == 'local' and before['revision'] is None and before['consent_saved']
    with db_setup() as db:
        owner = db.scalar(select(m.User))
        identity = c.selection_for(db, owner.id).identity
        consent_version, profile_version = owner.ai_consent_version, owner.updated_at
        assert db.get(m.AIConnection, owner.id) is None
    if not successful: state['status'] = 500
    response = client.post(B + '/ai/connection/test', headers=csrf(client, auth), json={'expected_revision': None})
    assert response.status_code == (200 if successful else 503)
    after = settings(client, auth)
    assert after['test_status'] == ('success' if successful else 'failed') and after['tested_at']
    assert after['mode'] == before['mode'] and after['model_id'] == before['model_id'] and after['consent_saved']
    assert after['revision'] and not after['has_key'] and len(calls) == 1
    if successful: assert response.json()['connection_revision'] == after['revision']
    with db_setup() as db:
        owner = db.scalar(select(m.User))
        assert (owner.ai_consent_version, owner.updated_at) == (consent_version, profile_version)
        assert c.selection_for(db, owner.id).identity == identity
        assert db.scalar(select(func.count()).select_from(m.Message)) == 0
    state['status'] = 200
    assert chat(client, auth).status_code == 200  # New context revision remains usable with unchanged consent.


def test_cookie_path_honored_and_bearer_session_csrf_bound(client, auth, external):
    refresh = next(cookie for cookie in client.cookies.jar if cookie.name == 'refresh_token')
    assert refresh.path == '/api/v1/auth' and refresh.has_nonstandard_attr('HttpOnly')
    result = save(client, auth)
    assert result.status_code == 200, result.text
    sent = result.request.headers.get('cookie', '')
    assert 'csrf_token=' in sent and 'refresh_token=' not in sent
    assert 'refresh_token=' in client.get(B + '/auth/me', headers=auth).request.headers['cookie']
    revision = result.json()['revision']
    client.cookies.set('csrf_token', 'synthetic-forged-csrf', domain=refresh.domain, path='/')
    assert save(client, auth).status_code == 403  # Matching cookie/header alone is insufficient.
    assert settings(client, auth)['revision'] == revision


def test_encrypted_masked_atomic_replace_and_remove(client, auth, external, db_setup, caplog):
    calls, _ = external
    result = save(client, auth)
    assert result.status_code == 200, result.text
    first = result.json(); assert first['has_key'] and not first['consent_saved'] and first['test_status'] == 'untested'
    assert KEY not in result.text and 'encrypted_key' not in result.text
    assert calls == []  # Saving/status are never billable probes.
    with db_setup() as db:
        selected = c.selection_for(db, first['user']['id'])
        ciphertext = db.get(m.AIConnection, selected.user_id).encrypted_key
        assert KEY not in ciphertext and ciphertext.startswith('v1:')
        assert c.decrypt_key(selected) == KEY
        assert KEY not in repr(selected)
    denied = save(client, auth, provider='custom', base_url='https://provider.example/v1', api_key=None)
    assert denied.status_code == 422
    assert settings(client, auth)['revision'] == first['revision']
    assert settings(client, auth)['provider'] == 'openai'
    stale = save(client, auth, expected_revision=None)
    assert stale.status_code == 409
    updated = save(client, auth, api_key=None, model_id='another-model').json()
    assert updated['revision'] != first['revision'] and updated['has_key']
    assert KEY not in json.dumps(settings(client, auth)) + caplog.text
    removed = client.request('DELETE', B + '/ai/connection', headers=csrf(client, auth), json={'expected_revision': updated['revision']})
    assert removed.status_code == 200 and not removed.json()['has_key'] and removed.json()['mode'] == 'disabled'
    with db_setup() as db:
        row = db.get(m.AIConnection, first['user']['id'])
        assert row.encrypted_key is None and row.provider is None and row.base_url is None
        assert row.revision not in (first['revision'], updated['revision'])
    assert chat(client, auth).status_code == 503 and calls == []


def test_isolation_auth_csrf_and_secret_errors(client, auth, register, external):
    saved = save(client, auth).json()
    other, _ = register('second-key-owner@example.com')
    own = settings(client, other)
    assert not own['has_key'] and own['revision'] is None
    assert client.get(B + '/ai/connection').status_code == 401
    assert client.put(B + '/ai/connection', headers=auth, json={}).status_code in (403, 422)
    assert save(client, other, expected_revision=saved['revision']).status_code == 409
    assert save(client, auth).status_code == 403  # Other owner's shared cookies cannot mutate A.
    response = client.put(B + '/ai/connection', headers=csrf(client, other), json={KEY: KEY})
    assert response.status_code == 422 and KEY not in response.text
    response = client.put(B + '/ai/connection', headers={**csrf(client, other), 'Origin': 'https://evil.example'}, json={})
    assert response.status_code == 403


@pytest.mark.parametrize('mutation', ['tamper', 'owner', 'endpoint', 'server_key'])
def test_authenticated_encryption_fails_closed(client, auth, external, db_setup, monkeypatch, mutation):
    from dataclasses import replace
    result = save(client, auth).json()
    with db_setup() as db:
        selected = c.selection_for(db, result['user']['id'])
    if mutation == 'tamper':
        selected = replace(selected, encrypted_key=selected.encrypted_key[:-5] + 'AAAAA')
    elif mutation == 'owner':
        selected = replace(selected, user_id='other-owner')
    elif mutation == 'endpoint':
        selected = replace(selected, base_url='https://elsewhere.example/v1')
    else:
        monkeypatch.setattr(get_settings(), 'ai_credential_key', SecretStr(base64.urlsafe_b64encode(b'z' * 32).decode()))
    with pytest.raises(Exception) as caught:
        c.decrypt_key(selected)
    assert caught.value.status_code == 503 and KEY not in str(caught.value)


@pytest.mark.parametrize('other_secret', ['secret_key', 'ai_token'])
def test_encryption_key_must_not_reuse_app_or_local_service_secret(client, external, monkeypatch, other_secret):
    config = get_settings()
    encoded = config.ai_credential_key.get_secret_value()
    monkeypatch.setattr(config, other_secret, SecretStr(encoded) if other_secret == 'ai_token' else encoded)
    with pytest.raises(Exception) as caught:
        c.encryption_key()
    assert caught.value.status_code == 503 and encoded not in str(caught.value)


def test_missing_admission_gate_fails_closed_before_provider_call(client, auth, external, db_setup):
    calls, _ = external
    assert save(client, auth).status_code == 200
    consent(client, auth)
    with db_setup.begin() as db:
        db.delete(db.get(m.AIGate, 1))
    response = chat(client, auth)
    assert response.status_code == 503 and response.json()['error']['code'] == 'ai_setup_required'
    assert calls == []
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []


def test_missing_setup_and_demo_reject_keys_without_breaking_finance(client, auth, external, monkeypatch):
    monkeypatch.setattr(get_settings(), 'ai_credential_key', None)
    assert not settings(client, auth)['external_available']
    assert save(client, auth).status_code == 503
    assert client.get(B + '/accounts', headers=auth).status_code == 200
    demo = client.post(B + '/auth/demo').json()
    headers = {'Authorization': 'Bearer ' + demo['access_token']}
    assert save(client, headers).status_code == 403


def test_success_test_status_history_provenance_and_consent(client, auth, external, db_setup):
    calls, _ = external
    saved = save(client, auth).json()
    assert chat(client, auth).status_code == 403 and not calls
    consent(client, auth)
    test = client.post(B + '/ai/connection/test', headers=csrf(client, auth), json={'expected_revision': saved['revision']})
    assert test.status_code == 200 and settings(client, auth)['test_status'] == 'success'
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []
    first = chat(client, auth)
    assert first.status_code == 200, first.text
    answer = first.json(); assert answer['metadata']['source'] == 'user_provider' and 'revision' not in answer['metadata']
    cid = answer['conversation_id']
    second = chat(client, auth, conversation_id=cid, text='Follow up')
    assert second.status_code == 200
    assert [x['role'] for x in calls[-1][2]['messages']] == ['system', 'user', 'assistant', 'user']
    assert calls[-1][2]['max_completion_tokens'] == 384 and calls[-1][2]['stream'] is False
    messages = client.get(f'{B}/advisor/conversations/{cid}/messages', headers=auth).json()
    assert messages[1]['generation_metadata']['model'] == 'test-model-snapshot'
    changed = save(client, auth, api_key=None, model_id='other-model').json()
    assert changed['test_status'] == 'untested' and not changed['consent_saved']
    consent(client, auth)
    assert chat(client, auth, conversation_id=cid).status_code == 409
    assert len(calls) == 3  # No old conversation transmitted to another model/destination.


@pytest.mark.parametrize('status,code', [(401, 'ai_invalid_key'), (403, 'ai_invalid_key'), (429, 'ai_provider_limited'),
    (400, 'ai_model_rejected'), (404, 'ai_model_rejected'), (500, 'ai_failed'), (503, 'ai_failed'), (504, 'ai_timeout'), (302, 'ai_failed')])
def test_provider_failures_no_partial_saves_no_retry_no_fallback(client, auth, external, monkeypatch, status, code, caplog):
    from app import ai
    calls, state = external
    save(client, auth); consent(client, auth)
    state['status'], state['body'] = status, {'error': KEY}
    monkeypatch.setattr(ai, 'send_message', lambda request: pytest.fail('Silent local fallback'))
    response = chat(client, auth)
    assert response.status_code in (503, 504) and response.json()['error']['code'] == code
    assert KEY not in response.text + caplog.text and len(calls) == 1
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []


@pytest.mark.parametrize('kind', ['network', 'timeout', 'malformed', 'empty', 'oversize', 'truncated', 'secret', 'missing_model'])
def test_invalid_provider_responses_fail_without_persistence(client, auth, external, kind):
    calls, state = external
    save(client, auth); consent(client, auth)
    if kind == 'network': state['exception'] = OSError(KEY)
    elif kind == 'timeout': state['exception'] = TimeoutError(KEY)
    elif kind == 'malformed': state['body'] = []
    elif kind == 'truncated': state['body']['choices'][0]['finish_reason'] = 'length'
    elif kind == 'missing_model': state['body'].pop('model')
    else: state['body']['choices'][0]['message']['content'] = {'empty': '', 'oversize': 'x'*6001, 'secret': KEY}[kind]
    response = chat(client, auth)
    assert response.status_code in (503, 504) and KEY not in response.text and len(calls) == 1
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []


@pytest.mark.parametrize('mutation', ['key', 'model', 'endpoint', 'remove_recreate', 'consent_regrant', 'logout', 'owner'])
def test_inflight_mutations_discard_response(client, auth, external, db_setup, mutation):
    calls, state = external
    save(client, auth); consent(client, auth)
    def mutate():
        if mutation == 'consent_regrant':
            client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': False}); consent(client, auth)
        elif mutation == 'logout':
            assert client.post(B + '/auth/logout', headers=csrf(client, auth)).status_code == 204
        elif mutation == 'owner':
            assert client.request('DELETE', B + '/auth/me', headers=auth, json={'password': 'correct horse battery'}).status_code == 204
        else:
            if mutation == 'remove_recreate':
                assert client.request('DELETE', B + '/ai/connection', headers=csrf(client, auth), json={'expected_revision': settings(client, auth)['revision']}).status_code == 200
            options = {'model_id': 'new-model'} if mutation == 'model' else {'api_key': KEY + '-new'}
            if mutation == 'endpoint': options.update(provider='custom', base_url='https://provider.example/v1')
            assert save(client, auth, **options).status_code == 200
            consent(client, auth)
    state['hook'] = mutate
    response = chat(client, auth)
    assert response.status_code == (401 if mutation in ('logout', 'owner') else 409), response.text
    with db_setup() as db:
        assert db.scalar(select(func.count()).select_from(m.Message)) == 0
        if mutation == 'owner':
            assert db.scalar(select(func.count()).select_from(m.AIConnection)) == 0
            assert db.scalar(select(func.count()).select_from(m.AIUsage)) == 0
    assert len(calls) == 1


def test_shared_quota_survives_key_changes_and_process_limiter_reset(client, auth, external, monkeypatch):
    calls, _ = external
    monkeypatch.setattr(get_settings(), 'ai_requests_per_day', 1)
    save(client, auth); consent(client, auth)
    assert chat(client, auth).status_code == 200
    save(client, auth, api_key=KEY + '-new'); consent(client, auth); limiter.entries.clear()
    response = chat(client, auth)
    assert response.status_code == 429 and response.json()['error']['code'] == 'ai_quota_reached' and len(calls) == 1


def test_inflight_lease_blocks_second_request_and_does_not_hold_db_lock(client, auth, external):
    calls, state = external
    save(client, auth); consent(client, auth)
    def during():
        state['hook'] = None
        response = chat(client, auth)
        assert response.status_code == 429 and response.json()['error']['code'] == 'ai_busy'
    state['hook'] = during
    assert chat(client, auth).status_code == 200 and len(calls) == 1
    assert chat(client, auth).status_code == 200 and len(calls) == 2


def test_expired_worker_cannot_publish_or_release_replacement_lease(client, auth, external, db_setup):
    _, state = external
    saved = save(client, auth).json(); consent(client, auth)
    replacement = m.uid()
    def during():
        with db_setup.begin() as db:
            usage = db.get(m.AIUsage, saved['user']['id'])
            usage.lease_token = replacement
            usage.lease_until = ai_limits.clock(db) + timedelta(seconds=60)
    state['hook'] = during
    response = chat(client, auth)
    assert response.status_code == 409 and response.json()['error']['code'] == 'ai_request_expired'
    with db_setup() as db:
        assert db.get(m.AIUsage, saved['user']['id']).lease_token == replacement
        assert db.scalar(select(func.count()).select_from(m.Message)) == 0
