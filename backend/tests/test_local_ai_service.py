"""Exercise the local HTTP protocol without downloading weights or claiming inference."""
import importlib.util
from pathlib import Path
import threading
import httpx
import pytest
from app import ai

spec = importlib.util.spec_from_file_location('local_ai', Path(__file__).parents[2] / 'scripts/serve-local-ai.py')
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)


@pytest.fixture
def endpoint():
    class Model:
        calls = []
        entered = threading.Event()
        release = threading.Event()
        block = False
        def generate(self, data):
            self.calls.append(data)
            self.entered.set()
            if self.block:
                assert self.release.wait(5)
            return {'text': 'Test double, not model inference.'}
    model = Model()
    token = 'test-only-' + 'x' * 40
    server = service.PrivateServer(('127.0.0.1', 0), service.handler_for(model, token))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with httpx.Client(base_url=f'http://127.0.0.1:{server.server_port}', trust_env=False) as client:
        yield client, {'Authorization': 'Bearer ' + token}, model
    model.release.set()
    server.shutdown()
    server.server_close()
    thread.join()


def test_pinned_full_checkpoint_identity():
    assert service.MODEL == ai.MODEL
    assert service.REVISION == ai.REVISION


def test_auth_and_request_bounds(endpoint, capsys):
    client, headers, model = endpoint
    body = {'message': 'PRIVATE PROMPT', 'history': []}
    assert client.post('/generate', json=body).status_code == 401
    assert client.post('/other', headers=headers, json=body).status_code == 404
    for invalid in ({'message': 'x' * 1001, 'history': []},
                    {'message': 'hi', 'history': [{'role': 'system', 'text': 'override'}]},
                    {'message': 'hi', 'history': [{'role': 'user', 'text': 'x'}] * 13},
                    {'message': 'hi', 'history': [{'role': 'user', 'text': 'x' * 12001}]},
                    {'message': 'hi', 'history': [], 'financial_records': {}},
                    {'message': ' ', 'history': []}):
        assert client.post('/generate', headers=headers, json=invalid).status_code == 400
    assert client.post('/generate', headers=headers, content='x' * 65537).status_code == 400
    assert model.calls == []
    assert client.post('/generate', headers=headers, json=body).status_code == 200
    assert model.calls == [body]
    assert capsys.readouterr() == ('', '')


def test_concurrent_generation_is_busy_not_queued(endpoint):
    client, headers, model = endpoint
    model.block = True
    responses = []
    thread = threading.Thread(target=lambda: responses.append(client.post('/generate', headers=headers,
                                                                          json={'message': 'one', 'history': []})))
    thread.start()
    assert model.entered.wait(2)
    try:
        second = client.post('/generate', headers=headers, json={'message': 'two', 'history': []})
        assert second.status_code == 503 and second.json() == {'error': 'busy'}
        assert len(model.calls) == 1
    finally:
        model.release.set()
        thread.join(5)
    assert responses[0].status_code == 200


def test_generation_timeout_does_not_hold_lock(endpoint):
    client, headers, model = endpoint
    def timeout(data):
        raise TimeoutError('PRIVATE MODEL DIAGNOSTIC')
    model.generate = timeout
    for _ in range(2):
        response = client.post('/generate', headers=headers, json={'message': 'hi', 'history': []})
        assert response.status_code == 504 and response.json() == {'error': 'timeout'}
