import pytest
from decimal import Decimal
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from sqlalchemy.exc import DataError
from app import ai, db as database, models as m
from app.config import get_settings
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


def test_postgres_driver_error_is_handled_without_prompt_leak(client, auth, db_setup, caplog):
    if db_setup.kw['bind'].dialect.name != 'postgresql':
        pytest.skip('PostgreSQL driver-specific regression; executed in parity suite')
    client.patch('/api/v1/auth/profile', headers=auth, json={'ai_consent': True})
    marker = 'PRIVATE_MARKER\x00'
    response = client.post('/api/v1/advisor/messages', headers=auth, json={'text': marker})
    assert response.status_code == 503
    assert 'PRIVATE_MARKER' not in response.text and 'PRIVATE_MARKER' not in caplog.text


def test_provider_selection_and_conversation_bound(client, auth, monkeypatch):
    assert isinstance(ai.get_provider(), ai.MockProvider)
    monkeypatch.setattr(get_settings(), 'ai_max_conversation_messages', 2)
    client.patch('/api/v1/auth/profile', headers=auth, json={'ai_consent': True})
    first = client.post('/api/v1/advisor/messages', headers=auth, json={'text': 'hello'}).json()
    response = client.post('/api/v1/advisor/messages', headers=auth, json={'text': 'again', 'conversation_id': first['conversation_id']})
    assert response.status_code == 409
    assert response.json()['error']['code'] == 'conversation_limit'
    monkeypatch.setattr(get_settings(), 'ai_mode', 'local')
    assert isinstance(ai.get_provider(), ai.LocalProvider)


def test_financial_context_is_opt_in_and_owner_only(client, auth, register, monkeypatch):
    from datetime import date
    prompts = []
    class SpyProvider:
        async def generate(self, text, system_prompt):
            prompts.append(system_prompt)
            return 'Educational fixture'
    monkeypatch.setattr(ai, 'get_provider', lambda: SpyProvider())
    for headers, amount in [(auth, '1234'), (register('context-other@example.com')[0], '9876')]:
        account = client.post('/api/v1/accounts', headers=headers, json={'name': 'Private account name', 'currency': 'USD'}).json()
        client.post('/api/v1/transactions', headers=headers, json={'account_id': account['id'], 'kind': 'income', 'amount': amount, 'category': 'Private category', 'description': 'Private record', 'occurred_on': date.today().isoformat()})
    client.patch('/api/v1/auth/profile', headers=auth, json={'ai_consent': True})
    client.post('/api/v1/advisor/messages', headers=auth, json={'text': 'hello'})
    assert prompts[-1] == ai.SYSTEM_PROMPT
    response = client.post('/api/v1/advisor/messages', headers=auth, json={'text': 'hello', 'include_financial_context': True})
    assert response.status_code == 201
    assert '1234.00' in prompts[-1] and '9876' not in prompts[-1]
    assert 'Private' not in prompts[-1]
    assert 'Verified backend monthly totals' in response.json()['text']


def test_slow_drip_provider_has_total_deadline(client, auth, monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers['Content-Length']))
            self.send_response(200)
            self.end_headers()
            try:
                for byte in b'{"text":"slow response"}':
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
                    time.sleep(.04)
            except (BrokenPipeError, ConnectionResetError):
                pass
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    config = get_settings()
    monkeypatch.setattr(config, 'ai_mode', 'local')
    monkeypatch.setattr(config, 'ai_local_url', f'http://127.0.0.1:{server.server_port}/chat')
    monkeypatch.setattr(config, 'ai_request_timeout_seconds', .2)
    client.patch('/api/v1/auth/profile', headers=auth, json={'ai_consent': True})
    try:
        start = time.monotonic()
        response = client.post('/api/v1/advisor/messages', headers=auth, json={'text': 'hello'})
        assert response.status_code == 502
        assert time.monotonic() - start < .7
        assert client.get('/api/v1/accounts', headers=auth).status_code == 200
        assert client.get('/api/v1/advisor/conversations', headers=auth).json() == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
