from dataclasses import asdict
from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from . import ai, models as m, schemas as s
from .db import get_db
from .security import current_user, limiter
from .config import get_settings
from .common import owned, pagination, public, rows

router = APIRouter(tags=['advisor'])


@router.get('/ai/health')
def ai_health(user=Depends(current_user)):
    return {'provider': 'unavailable', 'status': 'unavailable', 'is_demo': False}


@router.get('/advisor/context')
def context(user=Depends(current_user)):
    return {
        'status': 'unavailable',
        'welcome_message': {'role': 'assistant', 'text': ai.UNAVAILABLE_MESSAGE, 'is_demo': False},
        'starter_questions': ['How do I estimate zakat?', 'How can I plan giving?', 'What does uncertain screening mean?'],
    }


@router.post('/advisor/messages', status_code=503, response_model=ai.AIResult,
             responses={503: {'description': 'AI is not connected; nothing is saved'}})
def send_message(data: s.AdvisorMessage, user=Depends(current_user), db=Depends(get_db)):
    limiter.check(('advisor', user.id), get_settings().advisor_rate_limit)
    if data.conversation_id:
        owned(db, m.Conversation, data.conversation_id, user.id)
    # No consent or financial context is needed to report unavailability. Do not
    # create a conversation, load private history/totals, or persist failed sends.
    result = ai.send_message(ai.AIRequest(
        message=data.text,
        conversation_id=str(data.conversation_id) if data.conversation_id else None,
    ))
    return JSONResponse(asdict(result), status_code=503)


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
