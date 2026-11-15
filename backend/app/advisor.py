from urllib.parse import urlsplit, urlunsplit
from uuid import UUID
import httpx
from fastapi import APIRouter, Depends
from . import models as m, schemas as s
from .db import get_db
from .security import current_user, limiter
from .config import get_settings
from .common import fail, owned, pagination, public, rows

router = APIRouter(tags=['advisor'])
DISCLAIMER = 'Educational information only, not a religious ruling or personalized investment advice. Consult qualified professionals.'


def local_reply(text):
    config = get_settings()
    try:
        with httpx.Client(timeout=httpx.Timeout(10, connect=2), follow_redirects=False, trust_env=False) as client:
            with client.stream('POST', config.ai_local_url, json={'text': text}) as response:
                response.raise_for_status()
                content = bytearray()
                for chunk in response.iter_bytes():
                    content.extend(chunk)
                    if len(content) > 32768:
                        fail(502, 'ai_unavailable', 'Local advisor response exceeded size limit')
                import json
                payload = json.loads(content)
                answer = payload.get('text') if isinstance(payload, dict) else None
                if not isinstance(answer, str) or not answer.strip() or len(answer) > 8000:
                    fail(502, 'ai_unavailable', 'Local advisor returned an invalid response')
                return answer.strip() + '\n\n' + DISCLAIMER
    except (httpx.HTTPError, ValueError):
        fail(502, 'ai_unavailable', 'Local advisor unavailable; please retry later')


def mock_reply(text):
    if 'zakat' in text.lower():
        answer = 'Zakat commonly considers eligible wealth, a nisab threshold and the holding period. Use dated valuations and review asset and debt classification with a qualified scholar.'
    elif any(word in text.lower() for word in ['stock', 'invest', 'portfolio']):
        answer = 'Review business activities, financial ratios, diversification and risk. An uncertain screening result is not approval; manual quotes are not live prices.'
    else:
        answer = 'Track income and expenses by currency, build an emergency reserve and plan sustainable giving. This mock advisor does not inspect your financial records.'
    return answer + '\n\n' + DISCLAIMER


@router.get('/ai/health')
def ai_health(user=Depends(current_user)):
    config = get_settings()
    if config.ai_mode == 'mock':
        return {'provider': 'mock', 'status': 'available', 'is_demo': True}
    parts = urlsplit(config.ai_local_url)
    health_url = urlunsplit((parts.scheme, parts.netloc, '/health', '', ''))
    try:
        with httpx.Client(timeout=2, trust_env=False, follow_redirects=False) as client:
            response = client.get(health_url)
        available = 200 <= response.status_code < 300
    except httpx.HTTPError:
        available = False
    return {'provider': 'local', 'status': 'available' if available else 'unavailable', 'is_demo': False}


@router.get('/advisor/context')
def context(user=Depends(current_user)):
    return {'welcome_message': {'role': 'assistant', 'text': 'I can share educational budgeting, giving and screening information. ' + DISCLAIMER, 'is_demo': get_settings().ai_mode == 'mock'}, 'starter_questions': ['How do I estimate zakat?', 'How can I plan giving?', 'What does uncertain screening mean?']}


@router.post('/advisor/messages', status_code=201)
def send_message(data: s.AdvisorMessage, user=Depends(current_user), db=Depends(get_db)):
    if not user.ai_consent:
        fail(403, 'consent_required', 'Explicit advisor consent is required before sending a message')
    limiter.check(('advisor', user.id), get_settings().advisor_rate_limit)
    if data.conversation_id:
        conversation = owned(db, m.Conversation, data.conversation_id, user.id, lock=True)
    else:
        conversation = m.Conversation(user_id=user.id)
        db.add(conversation)
        db.flush()
    is_demo = get_settings().ai_mode == 'mock'
    answer = mock_reply(data.text) if is_demo else local_reply(data.text)
    db.add(m.Message(user_id=user.id, conversation_id=conversation.id, role='user', text=data.text, is_demo=is_demo))
    reply = m.Message(user_id=user.id, conversation_id=conversation.id, role='assistant', text=answer, is_demo=is_demo)
    db.add(reply)
    db.flush()
    return public(reply)


@router.get('/advisor/conversations')
def conversations(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [public(item) for item in rows(db, m.Conversation, user.id, page)]


@router.get('/advisor/conversations/{conversation_id}/messages')
def messages(conversation_id: UUID, page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    from sqlalchemy import select
    owned(db, m.Conversation, conversation_id, user.id)
    items = db.scalars(select(m.Message).where(m.Message.user_id == user.id, m.Message.conversation_id == str(conversation_id)).order_by(m.Message.created_at, m.Message.id).limit(page[0]).offset(page[1]))
    return [public(item) for item in items]


@router.delete('/advisor/conversations/{conversation_id}', status_code=204)
def delete_conversation(conversation_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    db.delete(owned(db, m.Conversation, conversation_id, user.id))
