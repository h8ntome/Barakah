import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import date, timedelta
import pytest
from sqlalchemy import select
from app import models as m
from app.config import get_settings
B = '/api/v1'


@pytest.fixture
def local_provider():
    state = {'requests': [], 'fail': False, 'oversize': False}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        def do_POST(self):
            state['requests'].append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
            self.send_response(503 if state['fail'] else 200)
            self.end_headers()
            self.wfile.write(json.dumps({'text': 'x' * 40000 if state['oversize'] else 'Local educational response'}).encode())
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}/chat', state
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_consent_mock_history_ownership_revocation(client, auth, register):
    assert client.get(B + '/ai/health', headers=auth).json()['is_demo'] is True
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'zakat'}).status_code == 403
    client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': True})
    response = client.post(B + '/advisor/messages', headers=auth, json={'text': 'zakat'}).json()
    assert response['is_demo'] and 'nisab' in response['text']
    conversation_id = response['conversation_id']
    history = client.get(B + '/advisor/conversations/' + conversation_id + '/messages', headers=auth).json()
    assert [message['role'] for message in history] == ['user', 'assistant']
    other, _ = register('other@example.com')
    client.patch(B + '/auth/profile', headers=other, json={'ai_consent': True})
    assert client.get(B + '/advisor/conversations/' + conversation_id + '/messages', headers=other).status_code == 404
    assert client.post(B + '/advisor/messages', headers=other, json={'text': 'hi', 'conversation_id': conversation_id}).status_code == 404
    client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': False})
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'zakat'}).status_code == 403
    assert client.delete(B + '/advisor/conversations/' + conversation_id, headers=auth).status_code == 204
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []


def test_local_http_adapter_only_current_text_failure_rollback(client, auth, local_provider, monkeypatch):
    url, state = local_provider
    monkeypatch.setattr(get_settings(), 'ai_mode', 'local')
    monkeypatch.setattr(get_settings(), 'ai_local_url', url)
    client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': True})
    assert client.get(B + '/ai/health', headers=auth).json()['status'] == 'available'
    response = client.post(B + '/advisor/messages', headers=auth, json={'text': 'hello'})
    assert response.status_code == 201
    assert response.json()['is_demo'] is False
    from app.ai import SYSTEM_PROMPT
    assert state['requests'] == [{'text': 'hello', 'system_prompt': SYSTEM_PROMPT}]
    state['fail'] = True
    failure = client.post(B + '/advisor/messages', headers=auth, json={'text': 'private text'})
    assert failure.status_code == 502 and 'private text' not in failure.text
    assert len(client.get(B + '/advisor/conversations', headers=auth).json()) == 1
    state['fail'], state['oversize'] = False, True
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'hi'}).status_code == 502


def test_advisor_input_limit_throttle(client, auth, monkeypatch):
    client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': True})
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': ' '}).status_code == 422
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'x' * 1001}).status_code == 422
    monkeypatch.setattr(get_settings(), 'advisor_rate_limit', 1)
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'hi'}).status_code == 201
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'hi'}).status_code == 429


def test_ads_approval_campaign_context_admin_aggregate(client, auth, db_setup):
    data = {'title': 'Educational sponsor', 'body': 'Sponsored message', 'url': 'https://example.com', 'context': 'education', 'active': True}
    assert client.post(B + '/admin/ads', headers=auth, json=data).status_code == 403
    with db_setup.begin() as db:
        db.scalar(select(m.User)).is_admin = True
    ad = client.post(B + '/admin/ads', headers=auth, json=data).json()
    assert client.get(B + '/ads?context=education', headers=auth).json() == []
    assert client.post(B + '/ads/' + ad['id'] + '/events', headers=auth, json={'kind': 'click'}).status_code == 404
    assert client.patch(B + '/admin/ads/' + ad['id'], headers=auth, json={'approved': True}).status_code == 200
    assert client.get(B + '/ads?context=dashboard', headers=auth).json() == []
    ads = client.get(B + '/ads?context=education', headers=auth).json()
    assert len(ads) == 1 and ads[0]['sponsored'] is True
    assert client.post(B + '/ads/' + ad['id'] + '/events', headers=auth, json={'kind': 'click'}).status_code == 201
    assert client.get(B + '/admin/ad-events', headers=auth).json()[0]['count'] == 1
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert client.patch(B + '/admin/ads/' + ad['id'], headers=auth, json={'starts_on': tomorrow}).status_code == 200
    assert client.get(B + '/ads?context=education', headers=auth).json() == []
    assert client.patch(B + '/admin/ads/' + ad['id'], headers=auth, json={'ends_on': '2000-01-01'}).status_code == 422
    assert client.patch(B + '/admin/ads/' + ad['id'], headers=auth, json={'url': 'javascript:alert(1)'}).status_code == 422


def test_security_headers_cors_body_limit(client, auth):
    response = client.options(B + '/auth/login', headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST'})
    assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
    assert response.headers['access-control-allow-credentials'] == 'true'
    assert client.post(B + '/accounts', headers={**auth, 'Origin': 'https://evil.example'}, json={'name': 'x', 'currency': 'USD'}).status_code == 403
    assert client.post(B + '/auth/login', content='x' * 70000).status_code == 413
    response = client.get('/health')
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert client.get(B + '/not-real').json()['error']['code'] == 'http_error'
