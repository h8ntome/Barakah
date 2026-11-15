"""Bounded OpenAI-compatible egress. No operator/provider key fallback."""
import ipaddress
import json
import re
import socket
import ssl
from urllib.parse import urlsplit
import anyio
import httpcore
from pydantic import ValidationError
from . import ai
from .config import get_settings

OPENAI_BASE = 'https://api.openai.com/v1'
SYSTEM_PROMPT = ('You are an educational finance assistant, not a financial adviser or religious scholar. '
                 'Do not certify investments or religious rulings. Verify arithmetic, explain uncertainty, '
                 'and refer individual decisions to qualified professionals. Do not recommend interest-bearing '
                 'products. Never request passwords or API keys. This project is a prototype and is not financial advice.')


def canonical_base(value):
    if not value or not value.isascii() or re.search(r'[\s\\%?#]', value):
        raise ValueError('Invalid endpoint')
    url = urlsplit(value)
    host = url.hostname or ''
    if (url.scheme != 'https' or url.username or url.password or url.port not in (None, 443)
            or not re.fullmatch(r'[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9]+(?:[a-z0-9-]*[a-z0-9])?)+', host)
            or not re.fullmatch(r'/[A-Za-z0-9_./-]*|', url.path)
            or any(part in {'.', '..'} for part in url.path.split('/')) or '//' in url.path):
        raise ValueError('Invalid endpoint')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('IP endpoints are forbidden')
    # Reject historical numeric IPv4 notations as well as ordinary IP literals.
    if all(re.fullmatch(r'(?:0x[0-9a-f]+|[0-9]+)', part) for part in host.split('.')):
        raise ValueError('Numeric endpoint')
    return 'https://' + host + url.path.rstrip('/')


def approved_base(provider, value):
    if provider == 'openai':
        if value and canonical_base(value) != OPENAI_BASE:
            raise ValueError('OpenAI endpoint is fixed')
        return OPENAI_BASE
    if provider != 'custom':
        raise ValueError('Unsupported provider')
    target = canonical_base(value)
    approved = {canonical_base(item.strip()) for item in get_settings().ai_allowed_base_urls.split(',') if item.strip()}
    if target not in approved:
        raise ValueError('Endpoint not approved')
    return target


def public_address(value):
    address = ipaddress.ip_address(value)
    if not address.is_global or address.is_multicast or address.is_reserved:
        raise ValueError('Non-public destination')
    if address.version == 6 and (address.ipv4_mapped or address.sixtofour or address.teredo
                                or address not in ipaddress.ip_network('2000::/3')):
        raise ValueError('Unsupported transition address')
    return str(address)


class PublicBackend(httpcore.AsyncNetworkBackend):
    def __init__(self, hostname):
        self.hostname = hostname

    async def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        if host != self.hostname or port != 443 or local_address:
            raise ValueError('Unexpected destination')
        with anyio.fail_after(min(timeout or 5, 5)):
            answers = await anyio.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            addresses = [public_address(answer[4][0]) for answer in answers]
            if not addresses:
                raise ValueError('No public destination')
            # Dial the validated numeric address, never resolve the hostname a second time.
            # httpcore retains the ORIGINAL hostname for Host, TLS SNI and certificate checks.
            return await httpcore.AnyIOBackend().connect_tcp(
                addresses[0], port, timeout=timeout, socket_options=socket_options)


async def exchange(base, credential, payload):
    body = json.dumps(payload, ensure_ascii=False).encode()
    if len(body) > 64000:
        raise ValueError('Input bounds')
    hostname = urlsplit(base).hostname
    # The cancellation scope includes DNS, TCP, TLS, headers and every body chunk.
    with anyio.fail_after(get_settings().external_ai_timeout_seconds):
        async with httpcore.AsyncConnectionPool(
                ssl_context=ssl.create_default_context(), network_backend=PublicBackend(hostname),
                max_connections=1, max_keepalive_connections=0, retries=0, http2=False) as pool:
            async with pool.stream('POST', base + '/chat/completions', content=body, headers={
                    'Authorization': 'Bearer ' + credential, 'Content-Type': 'application/json',
                    'Accept': 'application/json', 'Accept-Encoding': 'identity'}, extensions={
                    'timeout': {'connect': 5, 'read': 35, 'write': 5, 'pool': 1}}) as response:
                if response.status != 200:
                    return response.status, None  # Never read, log or return provider error bodies.
                headers = {k.lower(): v.lower() for k, v in response.headers}
                if headers.get(b'content-encoding', b'identity') != b'identity':
                    raise ValueError('Encoded response unsupported')
                content = bytearray()
                async for chunk in response.aiter_stream():
                    content.extend(chunk)
                    if len(content) > 40000:
                        raise ValueError('Response bounds')
                if credential.encode() in content:
                    raise ValueError('Credential-bearing response')
                return response.status, json.loads(content)


def reject_credentials(body, credential):
    pending = [body]
    while pending:
        item = pending.pop()
        if isinstance(item, str) and credential in item:
            raise ValueError('Credential-bearing response')
        if isinstance(item, dict):
            pending.extend(item.keys())
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def send(request, selection, credential):
    try:
        base = approved_base(selection.provider, selection.base_url)  # Recheck current operator policy on every send.
        if (not request.message.strip() or len(request.message) > 1000 or len(request.history) > ai.MAX_HISTORY
                or sum(len(item.text) for item in request.history) > ai.MAX_HISTORY_CHARS):
            raise ValueError('Input bounds')
        payload = {'model': selection.model_id, 'stream': False,
                   'messages': [{'role': 'system', 'content': SYSTEM_PROMPT}]
                   + [{'role': item.role, 'content': item.text} for item in request.history]
                   + [{'role': 'user', 'content': request.message}],
                   ('max_completion_tokens' if selection.provider == 'openai' else 'max_tokens'): 384}
        status, body = anyio.run(exchange, base, credential, payload)
        errors = {401: ('ai_invalid_key', 'Provider rejected the saved API key. Update it in Settings.'),
                  403: ('ai_invalid_key', 'Provider denied access. Check the saved key and model permissions.'),
                  429: ('ai_provider_limited', 'Provider rate or spending limit reached. No message was saved.'),
                  400: ('ai_model_rejected', 'Provider rejected the model or supported request options.'),
                  404: ('ai_model_rejected', 'Provider model or endpoint was not found.')}
        if status in errors:
            return ai.AIResult(request.conversation_id, error=ai.AIError(*errors[status]))
        if status in (408, 504):
            raise TimeoutError()
        if status != 200:
            raise ValueError('Provider failure')
        reject_credentials(body, credential)  # Includes JSON-unescaped metadata and keys, not just assistant text.
        if not isinstance(body, dict):
            raise ValueError('Invalid response object')
        choices = body['choices']
        if not isinstance(choices, list) or len(choices) != 1 or choices[0]['finish_reason'] != 'stop':
            raise ValueError('Incomplete response')
        message = choices[0]['message']
        content = message['content']
        if (message.get('role') != 'assistant' or message.get('tool_calls') or not isinstance(content, str)
                or not content.strip() or len(content) > ai.MAX_OUTPUT or credential in content):
            raise ValueError('Invalid response')
        usage = body.get('usage') or {}
        if not isinstance(usage, dict):
            raise ValueError('Invalid usage')
        reported_model = body.get('model')
        if not isinstance(reported_model, str) or not reported_model.strip():
            raise ValueError('Missing provider-reported model')
        metadata = ai.ExternalGenerationMetadata(provider=selection.provider,
            model=reported_model, configured_model=selection.model_id,
            input_tokens=usage.get('prompt_tokens'), output_tokens=usage.get('completion_tokens'))
        return ai.AIResult(request.conversation_id, ai.AIMessage('assistant', content), None, metadata)
    except (TimeoutError, httpcore.TimeoutException):
        return ai.AIResult(request.conversation_id, error=ai.AIError('ai_timeout', 'AI request timed out. No message was saved.'))
    except (httpcore.NetworkError, httpcore.ProtocolError, OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, RecursionError, ValidationError):
        return ai.AIResult(request.conversation_id, error=ai.AIError('ai_failed', 'AI response unavailable or invalid. No message was saved.'))
