from uuid import UUID
from sqlalchemy import select, func
from .ai import DISCLAIMER, generate_reply, provider_available
from fastapi import APIRouter, Depends
from . import models as m, schemas as s
from .db import get_db
from .security import current_user, limiter
from .config import get_settings
from .common import fail, owned, pagination, public, rows

router = APIRouter(tags=['advisor'])
@router.get('/ai/health')
def ai_health(user=Depends(current_user)):
    mode = get_settings().ai_mode
    return {'provider': mode, 'status': 'available' if provider_available() else 'unavailable', 'is_demo': mode == 'mock'}


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
    count = db.scalar(select(func.count()).select_from(m.Message).where(m.Message.conversation_id == conversation.id))
    if count + 2 > get_settings().ai_max_conversation_messages:
        fail(409, 'conversation_limit', 'This conversation is full; start a new conversation')
    is_demo = get_settings().ai_mode == 'mock'
    financial_context = None
    if data.include_financial_context:
        from .finance import dashboard
        summary = dashboard(month=None, user=user, db=db)
        financial_context = [{key: item[key] for key in ('currency', 'income', 'expenses', 'savings')} for item in summary['by_currency']]
    answer = generate_reply(data.text, financial_context)
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
