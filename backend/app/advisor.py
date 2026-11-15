from dataclasses import asdict
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, text, func
from fastapi.responses import JSONResponse
from . import ai, ai_connections as connections, ai_limits, models as m, schemas as s
from .db import get_db
from .security import current_user, limiter, bearer
from .config import get_settings
from .common import owned, pagination, public, rows, fail

router = APIRouter(tags=['advisor'])


@router.get('/ai/health')
def ai_health(user=Depends(current_user), db=Depends(get_db)):
    selected = connections.selection_for(db, user.id)
    if selected.mode == 'local' and get_settings().ai_mode == 'http':
        return {'provider': 'http', 'status': 'configured', 'is_demo': False,
                'model': ai.MODEL, 'revision': ai.REVISION}
    if selected.mode == 'external':
        return {'provider': selected.provider, 'status': 'configured' if connections.external_available() else 'unavailable',
                'is_demo': False, 'model': selected.model_id, 'connection_revision': selected.revision,
                'source': 'user_provider'}
    return {'provider': 'unavailable', 'status': 'unavailable', 'is_demo': False}


@router.get('/advisor/context')
def context(user=Depends(current_user), db=Depends(get_db)):
    selected = connections.selection_for(db, user.id)
    status = ai_health(user, db)
    configured = status['status'] == 'configured'
    return {
        'status': status['status'], 'provider': status['provider'], 'model': status.get('model'),
        'connection_revision': selected.revision,
        'welcome_message': {'role': 'assistant', 'text': ('AI endpoint configured, not a live availability check. Save consent in Settings before sending. Only your question and recent conversation history are sent; no financial records. Responses may be inaccurate.' if configured else ai.UNAVAILABLE_MESSAGE), 'is_demo': False},
        'starter_questions': ['How do I estimate zakat?', 'How can I plan giving?', 'What does uncertain screening mean?'],
    }


def history_snapshot(db, conversation_id, user_id):
    conditions = (m.Message.user_id == user_id, m.Message.conversation_id == conversation_id)
    count = db.scalar(select(func.count()).select_from(m.Message).where(*conditions))
    recent = list(db.scalars(select(m.Message).where(*conditions).order_by(
        m.Message.created_at.desc(), m.Message.id.desc()).limit(ai.MAX_HISTORY)))
    signature = (count, tuple((item.id, item.role, item.text) for item in recent))
    history, size = [], 0
    for item in recent:
        if item.role not in {'user', 'assistant'} or size + len(item.text) > ai.MAX_HISTORY_CHARS:
            break
        history.append(ai.AIMessage(item.role, item.text))
        size += len(item.text)
    return signature, tuple(reversed(history))


def result_response(result, status):
    body = asdict(result)
    if result.metadata is None:
        body.pop('metadata')
    else:
        body['metadata'] = result.metadata.model_dump()
    return JSONResponse(body, status_code=status)


@router.post('/advisor/messages', response_model=ai.AIResult,
             responses={503: {'model': ai.AIResult, 'description': 'Unavailable; nothing saved'}})
def send_message(data: s.AdvisorMessage, user=Depends(current_user), db=Depends(get_db),
                 credentials=Depends(bearer)):
    limiter.check(('advisor', user.id), get_settings().advisor_rate_limit)
    conversation_id = str(data.conversation_id) if data.conversation_id else None
    if conversation_id:
        owned(db, m.Conversation, conversation_id, user.id)
    user = ai_limits.lock_owner(db, user.id)
    selected = connections.selection_for(db, user.id)
    connections.check_revision(selected, data.connection_revision)
    if selected.mode == 'disabled':
        # No fallback, history loading, provider call or persistence in disabled mode.
        return result_response(ai.AIResult(conversation_id), 503)
    connections.require_usable(selected)
    if not user.ai_consent:
        fail(403, 'ai_consent_required', 'Save AI consent in Settings before sending. No message was saved.')
    if data.include_financial_context:
        fail(422, 'ai_context_unsupported', 'Financial record context is not supported. No message was saved.')
    user_id, profile_version, consent_version = user.id, user.updated_at, user.ai_consent_version
    if conversation_id:
        conversation = owned(db, m.Conversation, conversation_id, user_id)
        if ((conversation.connection_identity and conversation.connection_identity != selected.identity)
                or (conversation.connection_identity is None and selected.mode == 'external')):
            fail(409, 'ai_destination_changed', 'Start a new conversation for this provider/model. Old history will not be sent to a different destination.')
    signature, history = history_snapshot(db, conversation_id, user_id) if conversation_id else (None, ())
    duration = get_settings().ai_timeout_seconds if selected.mode == 'local' else get_settings().external_ai_timeout_seconds
    lease = ai_limits.reserve(db, user_id, duration)
    try:
        result = connections.generate(ai.AIRequest(data.text, conversation_id, history), selected)
        if result.error:
            return result_response(result, 504 if result.error.code == 'ai_timeout' else 503)
        owner, usage = connections.revalidate(db, selected, credentials, profile_version, consent_version, lease)
        if conversation_id:
            owned(db, m.Conversation, conversation_id, user_id, lock=True)
            if history_snapshot(db, conversation_id, user_id)[0] != signature:
                fail(409, 'ai_conversation_changed', 'Conversation changed during generation. No message was saved.')
        else:
            conversation = m.Conversation(user_id=user_id, connection_identity=selected.identity)
            db.add(conversation)
            db.flush()
            conversation_id = conversation.id
        for role, content in [('user', data.text), ('assistant', result.response.text)]:
            db.add(m.Message(user_id=user_id, conversation_id=conversation_id, role=role, text=content,
                             is_demo=False, generation_metadata=result.metadata.model_dump() if role == 'assistant' and result.metadata else None))
            db.flush()
        usage.lease_token = usage.lease_until = None
        db.commit()  # Messages, conversation and successful lease release are atomic.
        return result_response(ai.AIResult(conversation_id, result.response, None, result.metadata), 200)
    finally:
        ai_limits.release(db, user_id, lease)


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
