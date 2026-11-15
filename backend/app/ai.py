"""Unavailable-only AI boundary: no model, network transport or generated advice."""
from dataclasses import dataclass, field
from typing import Literal

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


@dataclass(frozen=True)
class AIResult:
    conversation_id: str | None
    response: AIMessage | None = None
    error: AIError | None = field(default_factory=AIError)


def send_message(request: AIRequest) -> AIResult:
    """Keep the integration contract without reading history or invoking a provider."""
    return AIResult(conversation_id=request.conversation_id)
