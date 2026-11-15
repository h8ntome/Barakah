"""Opt-in, bounded HTTP model boundary. Never receives financial records."""
from dataclasses import dataclass, field
from typing import Literal
import json
import time
import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from .config import get_settings

MODEL = 'h8notme/barakah1'
REVISION = '912a5697cf9d85adf065ee512f509cfa236459d4'
MAX_HISTORY = 12
MAX_HISTORY_CHARS = 12000
MAX_OUTPUT = 6000
UNAVAILABLE_MESSAGE = 'The AI assistant is not connected yet. No message was saved. Your other financial tools remain available.'


@dataclass(frozen=True)
class AIMessage:
    role: Literal['user', 'assistant']
    text: str


@dataclass(frozen=True)
class AIRequest:
    message: str
    conversation_id: str | None = None
    history: tuple[AIMessage, ...] = ()


@dataclass(frozen=True)
class AIError:
    code: str = 'ai_unavailable'
    message: str = UNAVAILABLE_MESSAGE


class GenerationMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    model: Literal['h8notme/barakah1']
    revision: Literal['912a5697cf9d85adf065ee512f509cfa236459d4']
    prompt_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    template_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    input_tokens: int = Field(ge=1, le=8192)
    output_tokens: int = Field(ge=1, le=384)
    generation_seconds: float = Field(ge=0, le=300, allow_inf_nan=False)


class ProviderResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    text: str = Field(min_length=1, max_length=MAX_OUTPUT)
    metadata: GenerationMetadata


@dataclass(frozen=True)
class AIResult:
    conversation_id: str | None
    response: AIMessage | None = None
    error: AIError | None = field(default_factory=AIError)
    metadata: GenerationMetadata | None = None


def send_message(request: AIRequest) -> AIResult:
    config = get_settings()
    if config.ai_mode != 'http':
        return AIResult(conversation_id=request.conversation_id)
    try:
        if (not request.message.strip() or len(request.message) > 1000
                or len(request.history) > MAX_HISTORY
                or sum(len(item.text) for item in request.history) > MAX_HISTORY_CHARS):
            raise ValueError('Request bounds')
        payload = {'message': request.message,
                   'history': [{'role': item.role, 'text': item.text} for item in request.history]}
        started = time.monotonic()
        # No redirects, environment proxies or retries; never expose provider errors.
        with httpx.Client(timeout=config.ai_timeout_seconds, trust_env=False) as client:
            with client.stream('POST', config.ai_url, json=payload,
                               headers={'Authorization': 'Bearer ' + config.ai_token.get_secret_value()}) as response:
                if response.status_code == 504:
                    raise httpx.ReadTimeout('Model generation deadline')
                response.raise_for_status()
                if response.headers.get('Content-Encoding', 'identity') != 'identity':
                    raise ValueError('Encoded response unsupported')
                body = bytearray()
                for chunk in response.iter_raw(chunk_size=4096):
                    body.extend(chunk)
                    if len(body) > 40000:
                        raise ValueError('Response bounds')
                    if time.monotonic() - started > config.ai_timeout_seconds:
                        raise httpx.ReadTimeout('Response deadline')
        parsed = ProviderResponse.model_validate(json.loads(body))
        if not parsed.text.strip():
            raise ValueError('Empty response')
        return AIResult(request.conversation_id, AIMessage('assistant', parsed.text), None, parsed.metadata)
    except httpx.TimeoutException:
        return AIResult(request.conversation_id, error=AIError('ai_timeout', 'AI request timed out. No message was saved.'))
    except (httpx.HTTPError, ValueError, ValidationError):
        return AIResult(request.conversation_id, error=AIError('ai_failed', 'AI response unavailable or invalid. No message was saved.'))
