import pytest
from decimal import Decimal
from sqlalchemy.exc import DataError
from app import ai, db as database, models as m
from app.config import Settings, get_settings
from app.portfolio import holding_view


def test_holding_gain_rounds_once():
    holding = m.Holding(quantity=Decimal('1'), quote_price=Decimal('1.005'), cost_basis=Decimal('1.004'))
    result = holding_view(holding)
    assert result['market_value'] == '1.01'
    assert result['unrealized_gain'] == '0.00'


def test_database_errors_do_not_escape_with_private_parameters(client, auth, monkeypatch, caplog):
    from app import finance
    marker = 'PRIVATE_FINANCIAL_MARKER'
    def broken(*args, **kwargs):
        raise DataError('insert into accounts', {'name': marker}, ValueError('driver rejected input'))
    monkeypatch.setattr(finance, 'rows', broken)
    response = client.get('/api/v1/accounts', headers=auth)
    assert response.status_code == 503
    assert marker not in response.text and marker not in caplog.text
    assert database.engine.hide_parameters is True


def test_unavailable_prompt_never_reaches_database_or_logs(client, auth, db_setup, caplog):
    from sqlalchemy import event
    statements = []
    engine = db_setup.kw['bind']
    def capture(connection, cursor, statement, parameters, context, executemany):
        statements.append((statement, parameters))
    event.listen(engine, 'before_cursor_execute', capture)
    try:
        marker = 'PRIVATE_MARKER\x00'
        response = client.post('/api/v1/advisor/messages', headers=auth, json={'text': marker})
        assert response.status_code == 503
        assert response.json()['error']['code'] == 'ai_unavailable'
        assert 'PRIVATE_MARKER' not in response.text + caplog.text + repr(statements)
        assert not any('INSERT' in sql.upper() for sql, _ in statements)
    finally:
        event.remove(engine, 'before_cursor_execute', capture)


@pytest.mark.parametrize('mode', ['mock', 'local', 'remote', ''])
def test_ai_configuration_rejects_every_connected_or_mock_mode(mode):
    with pytest.raises(ValueError):
        Settings(_env_file=None, ai_mode=mode)
    assert Settings(_env_file=None, ai_mode='unavailable').ai_mode == 'unavailable'


def test_ai_request_supports_history_without_generating_a_response():
    request = ai.AIRequest(message='Current private question', conversation_id='historical-id',
                           history=(ai.AIMessage(role='user', text='Old private question'),))
    result = ai.send_message(request)
    assert result.conversation_id == request.conversation_id
    assert result.response is None
    assert result.error.code == 'ai_unavailable'
    assert 'private' not in repr(result)


@pytest.mark.parametrize('include_context', [False, True])
def test_unavailable_never_loads_financial_context(client, auth, monkeypatch, include_context):
    from app import finance
    def forbidden(*args, **kwargs):
        pytest.fail('Unavailable AI must not load financial context')
    monkeypatch.setattr(finance, 'dashboard', forbidden)
    response = client.post('/api/v1/advisor/messages', headers=auth,
                           json={'text': 'hello', 'include_financial_context': include_context})
    assert response.status_code == 503
    assert response.json()['response'] is None


def test_unavailable_health_and_send_never_open_provider_transport(client, auth, monkeypatch):
    import httpx
    def forbidden(*args, **kwargs):
        pytest.fail('Unavailable AI must not create a provider HTTP client')
    monkeypatch.setattr(httpx, 'AsyncClient', forbidden)
    monkeypatch.setattr(httpx, 'Client', forbidden)
    # Even an in-process override cannot re-enable the removed providers.
    monkeypatch.setattr(get_settings(), 'ai_mode', 'local')
    assert client.get('/api/v1/ai/health', headers=auth).json()['status'] == 'unavailable'
    response = client.post('/api/v1/advisor/messages', headers=auth, json={'text': 'hello'})
    assert response.status_code == 503
    assert client.get('/api/v1/accounts', headers=auth).status_code == 200
    assert client.get('/api/v1/advisor/conversations', headers=auth).json() == []
