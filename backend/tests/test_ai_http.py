"""Opt-in HTTP advisor: transport, privacy, atomicity and in-flight revalidation."""
import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import select, func
from app import ai, models as m
from app.config import Settings, get_settings

B = '/api/v1'
METADATA = dict(model=ai.MODEL, revision=ai.REVISION, prompt_sha256='a' * 64,
                template_sha256='b' * 64, input_tokens=30, output_tokens=12,
                generation_seconds=0.25)


@pytest.fixture
def provider(monkeypatch, client):
    settings = get_settings()
    monkeypatch.setattr(settings, 'ai_mode', 'http')
    monkeypatch.setattr(settings, 'ai_url', 'http://127.0.0.1:8765/generate')
    monkeypatch.setattr(settings, 'ai_token', SecretStr('x' * 40))
    calls = []
    state = {'body': {'text': 'Educational response, not authoritative.', 'metadata': METADATA.copy()},
             'status': 200, 'hook': None, 'exception': None}
    real_client = httpx.Client

    def handle(request):
        import json
        calls.append(json.loads(request.content))
        assert request.headers['authorization'] == 'Bearer ' + 'x' * 40
        if state['hook']:
            state['hook']()
        if state['exception']:
            raise state['exception']
        return httpx.Response(state['status'], stream=httpx.ByteStream(json.dumps(state['body']).encode()))

    def transport(**kwargs):
        assert kwargs['timeout'] == settings.ai_timeout_seconds
        assert kwargs['trust_env'] is False
        return real_client(transport=httpx.MockTransport(handle), **kwargs)

    monkeypatch.setattr(ai.httpx, 'Client', transport)
    return calls, state


def consent(client, auth):
    assert client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': True}).status_code == 200


def counts(db_setup):
    with db_setup() as db:
        return tuple(db.scalar(select(func.count()).select_from(model)) for model in (m.Conversation, m.Message))


def test_configured_not_ready_and_saved_consent_required(client, auth, provider, db_setup):
    calls, _ = provider
    assert client.get(B + '/ai/health', headers=auth).json() == {
        'provider': 'http', 'status': 'configured', 'is_demo': False,
        'model': ai.MODEL, 'revision': ai.REVISION}
    assert client.get(B + '/advisor/context', headers=auth).json()['status'] == 'configured'
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'private'}).status_code == 403
    assert calls == [] and counts(db_setup) == (0, 0)
    consent(client, auth)
    assert client.post(B + '/advisor/messages', headers=auth,
                       json={'text': 'private', 'include_financial_context': True}).status_code == 422
    assert calls == [] and counts(db_setup) == (0, 0)


def test_success_followup_owner_history_and_no_financial_context(client, auth, register, provider, db_setup):
    calls, _ = provider
    consent(client, auth)
    client.post(B + '/accounts', headers=auth, json={'name': 'SECRET account', 'currency': 'USD', 'opening_balance': '999.00'})
    first = client.post(B + '/advisor/messages', headers=auth, json={'text': 'First question'})
    assert first.status_code == 200, first.text
    result = first.json()
    assert result['metadata'] == METADATA and result['error'] is None
    cid = result['conversation_id']
    other, _ = register('other-ai@example.com')
    consent(client, other)
    assert client.post(B + '/advisor/messages', headers=other,
                       json={'text': 'Steal history', 'conversation_id': cid}).status_code == 404
    assert len(calls) == 1
    followup = client.post(B + '/advisor/messages', headers=auth,
                           json={'text': 'Follow up', 'conversation_id': cid})
    assert followup.status_code == 200 and followup.json()['conversation_id'] == cid
    assert calls == [
        {'message': 'First question', 'history': []},
        {'message': 'Follow up', 'history': [
            {'role': 'user', 'text': 'First question'},
            {'role': 'assistant', 'text': result['response']['text']}]}]
    assert counts(db_setup) == (1, 4)
    saved = client.get(f'{B}/advisor/conversations/{cid}/messages', headers=auth).json()
    assert [item['role'] for item in saved] == ['user', 'assistant', 'user', 'assistant']
    assert all(item['is_demo'] is False for item in saved)
    assert client.get(f'{B}/advisor/conversations/{cid}/messages', headers=other).status_code == 404


@pytest.mark.parametrize('failure', ['timeout', 'connection', 'busy', 'model', 'revision', 'oversize', 'empty', 'metadata'])
def test_failures_never_save_or_retry(client, auth, provider, db_setup, historical_conversation, failure, caplog):
    calls, state = provider
    consent(client, auth)
    cid = historical_conversation()
    before = client.get(f'{B}/advisor/conversations/{cid}/messages', headers=auth).json()
    if failure == 'timeout':
        state['exception'] = httpx.ReadTimeout('PRIVATE transport diagnostic')
    elif failure == 'connection':
        state['exception'] = httpx.ConnectError('PRIVATE transport diagnostic')
    elif failure == 'busy':
        state['status'] = 503
    elif failure in {'model', 'revision'}:
        state['body']['metadata'][failure] = 'wrong'
    elif failure == 'metadata':
        state['body']['metadata']['output_tokens'] = 385
    else:
        state['body']['text'] = 'x' * 6001 if failure == 'oversize' else ' '
    for conversation in (None, cid):
        response = client.post(B + '/advisor/messages', headers=auth,
                               json={'text': 'PRIVATE prompt', 'conversation_id': conversation})
        assert response.status_code == (504 if failure == 'timeout' else 503)
        assert response.json()['response'] is None
        assert 'PRIVATE' not in response.text + caplog.text
        assert counts(db_setup) == (1, 2)
    assert len(calls) == 2  # One attempt per explicit send.
    assert client.get(f'{B}/advisor/conversations/{cid}/messages', headers=auth).json() == before
    assert client.get(B + '/accounts', headers=auth).status_code == 200


@pytest.mark.parametrize('mutation', ['consent', 'session', 'delete', 'append', 'owner'])
def test_inflight_changes_revalidated_without_holding_sqlite_lock(client, auth, provider, db_setup, historical_conversation, mutation):
    _, state = provider
    consent(client, auth)
    cid = historical_conversation()
    def mutate():
        # Separate connection must be able to commit while generation is in flight.
        with db_setup.begin() as db:
            if mutation == 'consent':
                db.scalar(select(m.User)).ai_consent = False
            elif mutation == 'session':
                db.scalar(select(m.Session)).revoked = True
            elif mutation == 'delete':
                db.delete(db.get(m.Conversation, cid))
            elif mutation == 'owner':
                db.delete(db.scalar(select(m.User)))
            else:
                db.add(m.Message(user_id=db.scalar(select(m.User.id)), conversation_id=cid,
                                 role='user', text='Concurrent message', is_demo=False))
    state['hook'] = mutate
    response = client.post(B + '/advisor/messages', headers=auth,
                           json={'text': 'Must not save', 'conversation_id': cid})
    assert response.status_code == {'consent': 409, 'session': 401, 'delete': 404, 'append': 409, 'owner': 401}[mutation]
    assert counts(db_setup) == ((0, 0) if mutation in {'delete', 'owner'} else (1, 3 if mutation == 'append' else 2))
    with db_setup() as db:
        assert db.scalar(select(func.count()).select_from(m.Message).where(m.Message.text == 'Must not save')) == 0


def test_history_is_bounded(client, auth, provider, db_setup, historical_conversation):
    calls, _ = provider
    consent(client, auth)
    cid = historical_conversation()
    with db_setup.begin() as db:
        uid = db.scalar(select(m.User.id))
        for _ in range(20):
            db.add(m.Message(user_id=uid, conversation_id=cid, role='assistant', text='x' * 2000, is_demo=False))
            db.flush()
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'hi', 'conversation_id': cid}).status_code == 200
    assert len(calls[0]['history']) <= 12
    assert sum(len(item['text']) for item in calls[0]['history']) <= 12000


@pytest.mark.parametrize('overrides', [
    {}, {'ai_url': 'http://example.com:8765/generate'}, {'ai_url': 'http://0.0.0.0:8765/generate'},
    {'ai_url': 'http://127.0.0.1:8765/generate?token=x'}, {'ai_url': 'http://user@127.0.0.1:8765/generate'},
    {'ai_url': 'http://127.0.0.1:8765/other'}, {'ai_token': 'short'},
    {'ai_token': 'x' * 40 + '\n'}, {'ai_token': 'é' * 40},
    {'ai_timeout_seconds': 0}, {'ai_timeout_seconds': 301}, {'ai_timeout_seconds': float('nan')},
])
def test_http_config_validation(overrides):
    kwargs = dict(ai_mode='http', ai_url='http://127.0.0.1:8765/generate', ai_token='x' * 40)
    if not overrides:
        kwargs.pop('ai_token')
    kwargs.update(overrides)
    with pytest.raises(ValueError):
        Settings(_env_file=None, **kwargs)


def test_http_config_valid_and_default_unavailable():
    assert Settings(_env_file=None).ai_mode == 'unavailable'
    config = Settings(_env_file=None, ai_mode='http', ai_url='http://127.0.0.1:8765/generate', ai_token='x' * 40)
    assert config.ai_mode == 'http' and 'x' * 40 not in repr(config)


def test_persistence_error_rolls_back_both_messages_and_conversation(client, auth, provider, db_setup):
    from sqlalchemy import event
    from sqlalchemy.exc import OperationalError
    consent(client, auth)
    engine = db_setup.kw['bind']
    inserts = []
    def fail_second_message(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith('INSERT INTO messages'):
            inserts.append(statement)
            if len(inserts) == 2:
                raise OperationalError('private insert', {}, Exception('private failure'))
    event.listen(engine, 'before_cursor_execute', fail_second_message)
    try:
        response = client.post(B + '/advisor/messages', headers=auth, json={'text': 'Do not partially save'})
        assert response.status_code == 503
    finally:
        event.remove(engine, 'before_cursor_execute', fail_second_message)
    assert len(inserts) == 2 and counts(db_setup) == (0, 0)
