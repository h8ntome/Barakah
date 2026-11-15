"""Real local TLS/HTTP sockets behind a test-only public-IP dial bridge; no external provider calls."""
import json
import socket
import ssl
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import anyio
import httpcore
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from app import external_ai as e
from app.config import get_settings
from test_ai_connections import external, save, consent, chat, csrf, settings, B

REAL_EXCHANGE = e.exchange
KEY = 'synthetic-transport-credential-' + 'x' * 20


@pytest.fixture
def tls_provider(tmp_path, monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'provider.example')])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=1)).add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .add_extension(x509.SubjectAlternativeName([x509.DNSName('provider.example')]), critical=False).sign(key, hashes.SHA256()))
    cert_path, key_path = tmp_path / 'cert.pem', tmp_path / 'key.pem'
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    state = {'requests': [], 'sni': [], 'dials': [], 'dns': [], 'trust': True, 'status': 200,
             'headers': {}, 'body': b'{"model":"reported-snapshot","choices":[{"finish_reason":"stop","message":{"role":"assistant","content":"synthetic reply"}}]}',
             'header_delay': 0, 'chunk_delay': 0, 'dns_delay': 0, 'tcp_delay': 0, 'tls_delay': 0}
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(cert_path, key_path)
    server_context.set_servername_callback(lambda sock, name, ctx: state['sni'].append(name))

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        def log_message(self, *args):
            pass
        def handle(self):
            try:
                super().handle()
            except (ConnectionResetError, ssl.SSLError):
                pass  # Client cancellation during deadline/TLS tests is expected.
        def do_POST(self):
            state['requests'].append({'host': self.headers['Host'], 'path': self.path,
                'authorization': self.headers['Authorization'], 'body': json.loads(self.rfile.read(int(self.headers['Content-Length'])))})
            try:
                time.sleep(state['header_delay'])
                self.send_response(state['status'])
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(state['body'])))
                for name, value in state['headers'].items(): self.send_header(name, value)
                self.end_headers()
                if state['chunk_delay']:
                    for byte in state['body']:
                        self.wfile.write(bytes([byte])); self.wfile.flush(); time.sleep(state['chunk_delay'])
                else:
                    self.wfile.write(state['body']); self.wfile.flush()
            except (OSError, ssl.SSLError):
                pass  # Deadline/certificate tests deliberately close the client socket.

    class Server(ThreadingHTTPServer):
        daemon_threads = True
        def get_request(self):
            conn, address = super().get_request()
            conn.settimeout(2)
            try:
                time.sleep(state['tls_delay'])
                return server_context.wrap_socket(conn, server_side=True), address
            except BaseException:
                conn.close()
                raise

    server = Server(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.02}, daemon=True)
    worker.start()
    original_context = ssl.create_default_context
    def context(*args, **kwargs):
        ctx = original_context(*args, **kwargs)
        if state['trust']: ctx.load_verify_locations(cafile=str(cert_path))
        assert ctx.check_hostname and ctx.verify_mode == ssl.CERT_REQUIRED
        return ctx
    monkeypatch.setattr(e.ssl, 'create_default_context', context)
    async def dns(host, port, **kwargs):
        state['dns'].append(host)
        await anyio.sleep(state['dns_delay'])
        # A second resolution would rebind to loopback. Production must dial the first validated numeric IP.
        address = '8.8.8.8' if len(state['dns']) == 1 else '127.0.0.1'
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (address, port))]
    monkeypatch.setattr(e.anyio, 'getaddrinfo', dns)
    original_connect = httpcore.AnyIOBackend.connect_tcp
    async def bridge(self, host, port, **kwargs):
        state['dials'].append((host, port))
        assert (host, port) == ('8.8.8.8', 443)
        await anyio.sleep(state['tcp_delay'])
        return await original_connect(self, '127.0.0.1', server.server_port, **kwargs)
    monkeypatch.setattr(httpcore.AnyIOBackend, 'connect_tcp', bridge)
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        monkeypatch.setenv(name, 'http://127.0.0.1:1')
    monkeypatch.setattr(get_settings(), 'external_ai_timeout_seconds', 2)
    try:
        yield state
    finally:
        server.shutdown(); server.server_close(); worker.join(timeout=3)


def test_real_tls_sni_host_public_dial_no_rebinding_or_proxy(tls_provider):
    status, body = anyio.run(e.exchange, 'https://provider.example/v1', KEY, {'model': 'requested-alias'})
    assert status == 200 and body['model'] == 'reported-snapshot'
    assert tls_provider['dns'] == ['provider.example']
    assert tls_provider['dials'] == [('8.8.8.8', 443)]
    assert tls_provider['sni'] == ['provider.example']
    assert tls_provider['requests'] == [{'host': 'provider.example', 'path': '/v1/chat/completions',
        'authorization': 'Bearer ' + KEY, 'body': {'model': 'requested-alias'}}]


@pytest.mark.parametrize('case', ['hostname', 'untrusted'])
def test_real_tls_certificate_and_hostname_verification(tls_provider, case):
    tls_provider['trust'] = case != 'untrusted'
    host = 'wrong.example' if case == 'hostname' else 'provider.example'
    with pytest.raises(httpcore.ConnectError):
        anyio.run(e.exchange, f'https://{host}/v1', KEY, {})
    assert tls_provider['sni'] == [host] and not tls_provider['requests']
    assert len(tls_provider['dials']) == 1  # No retry.


@pytest.mark.parametrize('stage', ['dns', 'tcp', 'tls', 'header', 'chunk'])
def test_total_deadline_includes_every_transport_stage(tls_provider, monkeypatch, stage):
    monkeypatch.setattr(get_settings(), 'external_ai_timeout_seconds', 0.15)
    tls_provider[stage + '_delay'] = 0.6 if stage != 'chunk' else 0.02
    started = time.monotonic()
    with pytest.raises(TimeoutError):
        anyio.run(e.exchange, 'https://provider.example/v1', KEY, {})
    assert time.monotonic() - started < 0.5  # Slow drip stays below per-read timeout but exceeds total budget.
    assert len(tls_provider['dials']) <= 1


@pytest.mark.parametrize('case', ['redirect', 'compressed', 'oversized', 'raw_secret'])
def test_real_transport_response_boundaries(tls_provider, case):
    if case == 'redirect':
        tls_provider['status'] = 307
        tls_provider['headers'] = {'Location': 'http://127.0.0.1/internal'}
        tls_provider['body'] = KEY.encode()
        assert anyio.run(e.exchange, 'https://provider.example/v1', KEY, {}) == (307, None)
    else:
        if case == 'compressed': tls_provider['headers'] = {'Content-Encoding': 'gzip'}
        elif case == 'oversized': tls_provider['body'] = b'x' * 40001
        else: tls_provider['body'] = json.dumps({'model': KEY}).encode()
        with pytest.raises(ValueError):
            anyio.run(e.exchange, 'https://provider.example/v1', KEY, {})
    assert len(tls_provider['requests']) == len(tls_provider['dials']) == 1


@pytest.mark.parametrize('value', ['http://provider.example/v1', 'https://user:pass@provider.example/v1',
    'https://provider.example:8443/v1', 'https://provider.example/v1?key=x', 'https://provider.example/v1#fragment',
    'https://provider.example/%2e%2e/private', 'https://provider.example/../private', 'https://provider.example//v1',
    'https://provider.example\\@evil.example', 'https://provider.example\n/v1', 'https://provider.example./v1',
    'https://*.provider.example/v1', 'https://127.0.0.1/v1', 'https://127.1/v1', 'https://2130706433/v1',
    'https://0x7f.0.0.1/v1', 'https://[::1]/v1', 'https://[fe80::1%en0]/v1', 'https://prövider.example/v1'])
def test_reject_ambiguous_endpoint_syntax(value):
    with pytest.raises(ValueError): e.canonical_base(value)


@pytest.mark.parametrize('value', ['127.0.0.1', '10.0.0.1', '172.16.1.1', '192.168.1.1', '169.254.169.254',
    '100.64.0.1', '0.0.0.0', '192.0.2.1', '224.0.0.1', '::1', '::', 'fc00::1', 'fe80::1', 'ff02::1',
    '::ffff:8.8.8.8', '2002:0808:0808::', '64:ff9b::808:808', '2001:db8::1'])
def test_nonpublic_or_transition_address_rejected_before_dial(monkeypatch, value):
    async def dns(*args, **kwargs):
        # Reject the entire answer set, not just a convenient public first answer.
        return [(2, 1, 6, '', ('8.8.8.8', 443)), (2, 1, 6, '', (value, 443))]
    async def forbidden(*args, **kwargs):
        pytest.fail('Unsafe DNS answer was dialed')
    monkeypatch.setattr(e.anyio, 'getaddrinfo', dns)
    monkeypatch.setattr(httpcore.AnyIOBackend, 'connect_tcp', forbidden)
    with pytest.raises(ValueError):
        anyio.run(e.PublicBackend('provider.example').connect_tcp, 'provider.example', 443)


@pytest.mark.parametrize('field', ['model', 'nested_value', 'object_key'])
@pytest.mark.parametrize('route', ['chat', 'test'])
def test_unicode_escaped_credential_rejected_across_decoded_response(client, auth, external, tls_provider, monkeypatch, caplog, field, route):
    monkeypatch.setattr(e, 'exchange', REAL_EXCHANGE)
    assert save(client, auth, provider='custom', base_url='https://provider.example/v1', api_key=KEY).status_code == 200
    consent(client, auth)
    body = json.loads(tls_provider['body'])
    if field == 'model': body['model'] = KEY
    elif field == 'nested_value': body['extra'] = [{'value': KEY}]
    else: body[KEY] = 'unused'
    tls_provider['body'] = json.dumps(body).replace(KEY, ''.join('\\u%04x' % ord(char) for char in KEY)).encode()
    assert KEY.encode() not in tls_provider['body']
    response = chat(client, auth) if route == 'chat' else client.post(B + '/ai/connection/test', headers=csrf(client, auth), json={'expected_revision': settings(client, auth)['revision']})
    assert response.status_code == 503 and response.json()['error']['code'] == 'ai_failed'
    history = client.get(B + '/advisor/conversations', headers=auth)
    assert history.json() == [] and len(tls_provider['requests']) == 1
    assert KEY not in response.text + history.text + json.dumps(settings(client, auth)) + caplog.text


def test_provider_reported_snapshot_is_separate_from_requested_alias(client, auth, external, tls_provider, monkeypatch):
    monkeypatch.setattr(e, 'exchange', REAL_EXCHANGE)
    assert save(client, auth, provider='custom', base_url='https://provider.example/v1', api_key=KEY, model_id='requested-alias').status_code == 200
    consent(client, auth)
    response = chat(client, auth)
    assert response.status_code == 200, response.text
    metadata = response.json()['metadata']
    assert metadata['model'] == 'reported-snapshot' and metadata['configured_model'] == 'requested-alias'
    assert metadata['source'] == 'user_provider' and 'revision' not in metadata


def test_failed_test_persists_safe_status_without_history(client, auth, external, tls_provider, monkeypatch):
    monkeypatch.setattr(e, 'exchange', REAL_EXCHANGE)
    assert save(client, auth, provider='custom', base_url='https://provider.example/v1', api_key=KEY).status_code == 200
    consent(client, auth)
    tls_provider['status'], tls_provider['body'] = 401, KEY.encode()
    response = client.post(B + '/ai/connection/test', headers=csrf(client, auth), json={'expected_revision': settings(client, auth)['revision']})
    assert response.status_code == 503 and response.json()['error']['code'] == 'ai_invalid_key'
    saved = settings(client, auth)
    assert saved['test_status'] == 'failed' and saved['test_error'] == 'ai_invalid_key' and saved['tested_at']
    assert KEY not in response.text + json.dumps(saved)
    assert client.get(B + '/advisor/conversations', headers=auth).json() == []


def test_exact_operator_allowlist(monkeypatch):
    monkeypatch.setattr(get_settings(), 'ai_allowed_base_urls', 'https://provider.example/v1')
    assert e.approved_base('custom', 'https://provider.example:443/v1/') == 'https://provider.example/v1'
    for candidate in ('https://provider.example.evil.example/v1', 'https://sub.provider.example/v1', 'https://provider.example/v2'):
        with pytest.raises(ValueError): e.approved_base('custom', candidate)
    with pytest.raises(ValueError): e.approved_base('openai', 'https://provider.example/v1')
