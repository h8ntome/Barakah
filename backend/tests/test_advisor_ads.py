from datetime import date, timedelta
import pytest
from sqlalchemy import select, func
from app import ai, models as m
from app.config import get_settings
B = '/api/v1'


@pytest.mark.parametrize('consent', [False, True])
def test_unavailable_send_never_persists_with_or_without_consent(client, auth, db_setup, consent):
    client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': consent})
    assert client.get(B + '/ai/health', headers=auth).json() == {
        'provider': 'unavailable', 'status': 'unavailable', 'is_demo': False}
    context = client.get(B + '/advisor/context', headers=auth).json()
    assert context['status'] == 'unavailable'
    assert context['welcome_message']['text'] == ai.UNAVAILABLE_MESSAGE
    assert context['starter_questions']
    response = client.post(B + '/advisor/messages', headers=auth, json={'text': 'PRIVATE question'})
    assert response.status_code == 503
    assert response.json() == {'conversation_id': None, 'response': None,
                               'error': {'code': 'ai_unavailable', 'message': ai.UNAVAILABLE_MESSAGE}}
    assert 'PRIVATE' not in response.text
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []
    with db_setup() as db:
        for model in (m.Conversation, m.Message):
            assert db.scalar(select(func.count()).select_from(model)) == 0


def test_historical_history_ownership_revocation_delete(client, auth, register, historical_conversation, db_setup):
    conversation_id = historical_conversation()
    path = B + '/advisor/conversations/' + conversation_id
    before = client.get(path + '/messages', headers=auth).json()
    assert [message['role'] for message in before] == ['user', 'assistant']
    assert client.get(path + '/messages?limit=1&offset=1', headers=auth).json() == before[1:]
    other, _ = register('other@example.com')
    assert client.get(B + '/advisor/conversations', headers=other).json() == []
    assert client.get(path + '/messages', headers=other).status_code == 404
    assert client.delete(path, headers=other).status_code == 404
    assert client.post(B + '/advisor/messages', headers=other, json={'text': 'hi', 'conversation_id': conversation_id}).status_code == 404
    for consent in (True, False):
        client.patch(B + '/auth/profile', headers=auth, json={'ai_consent': consent})
        response = client.post(B + '/advisor/messages', headers=auth, json={'text': 'hi', 'conversation_id': conversation_id})
        assert response.status_code == 503
        assert response.json()['conversation_id'] == conversation_id
        assert response.json()['error']['code'] == 'ai_unavailable'
        assert client.get(path + '/messages', headers=auth).json() == before
    assert client.delete(path, headers=auth).status_code == 204
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []
    with db_setup() as db:
        assert db.scalar(select(func.count()).select_from(m.Message)) == 0


def test_advisor_endpoints_require_authentication(client, auth, historical_conversation):
    conversation_id = historical_conversation()
    for method, path, body in [
        ('GET', '/ai/health', None), ('GET', '/advisor/context', None),
        ('GET', '/advisor/conversations', None),
        ('GET', f'/advisor/conversations/{conversation_id}/messages', None),
        ('DELETE', f'/advisor/conversations/{conversation_id}', None),
        ('POST', '/advisor/messages', {'text': 'hello'}),
    ]:
        assert client.request(method, B + path, json=body).status_code == 401


def test_advisor_openapi_documents_unavailable_result(client):
    responses = client.get('/openapi.json').json()['paths'][B + '/advisor/messages']['post']['responses']
    assert '200' not in responses and '201' not in responses
    assert responses['503']['content']['application/json']['schema']['$ref'].endswith('/AIResult')


def test_advisor_input_limit_throttle(client, auth, monkeypatch):
    for body in ({'text': ' '}, {'text': 'x' * 1001}, {'text': 'hi', 'conversation_id': 'invalid'}):
        assert client.post(B + '/advisor/messages', headers=auth, json=body).status_code == 422
    monkeypatch.setattr(get_settings(), 'advisor_rate_limit', 1)
    assert client.post(B + '/advisor/messages', headers=auth, json={'text': 'hi'}).status_code == 503
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
