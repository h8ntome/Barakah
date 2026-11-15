"""Owner-only encrypted connection configuration. Explicit serializers never return ciphertext."""
import base64
from dataclasses import dataclass, field
import hashlib
import json
import secrets
from fastapi import APIRouter, Depends, Request
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select, text
from . import ai, external_ai, ai_limits, models as m, schemas as s
from .common import fail, json_value
from .config import get_settings
from .db import get_db
from .security import current_user, access_session, csrf_token, digest, bearer, user_view

router = APIRouter(prefix='/ai/connection', tags=['AI connection'])


def encryption_key():
    config = get_settings()
    try:
        encoded = config.ai_credential_key.get_secret_value() if config.ai_credential_key else ''
        key = base64.b64decode(encoded, altchars=b'-_', validate=True)
        local_token = config.ai_token.get_secret_value() if config.ai_token else None
        if len(key) != 32 or encoded in (config.secret_key, local_token):
            raise ValueError('Invalid dedicated key')
        return key
    except (ValueError, TypeError):
        fail(503, 'ai_setup_required', 'The operator must configure the dedicated AI credential encryption key.')


def external_available():
    if not get_settings().user_ai_enabled:
        return False
    try:
        encryption_key()
        return True
    except Exception:
        return False


def associated_data(user_id, provider, base_url, revision):
    return json.dumps(['barakah-ai-v1', user_id, provider, base_url, revision], separators=(',', ':')).encode()


def encrypt_key(raw, user_id, provider, base_url, revision):
    nonce = secrets.token_bytes(12)
    sealed = AESGCM(encryption_key()).encrypt(nonce, raw.encode(), associated_data(user_id, provider, base_url, revision))
    return 'v1:' + base64.urlsafe_b64encode(nonce + sealed).decode()


def decrypt_key(selection):
    try:
        if not selection.encrypted_key or not selection.encrypted_key.startswith('v1:'):
            raise ValueError('Unknown ciphertext format')
        blob = base64.b64decode(selection.encrypted_key[3:], altchars=b'-_', validate=True)
        return AESGCM(encryption_key()).decrypt(blob[:12], blob[12:], associated_data(
            selection.user_id, selection.provider, selection.base_url, selection.revision)).decode()
    except (ValueError, TypeError, InvalidTag, UnicodeError):
        fail(503, 'ai_credentials_unavailable', 'The saved AI credential cannot be opened. Contact the operator or replace it.')


@dataclass(frozen=True)
class Selection:
    user_id: str
    mode: str
    revision: str | None
    provider: str | None = None
    base_url: str | None = None
    model_id: str | None = None
    encrypted_key: str | None = field(default=None, repr=False)

    @property
    def identity(self):
        data = ['local', ai.MODEL, ai.REVISION] if self.mode == 'local' else [self.provider, self.base_url, self.model_id]
        return hashlib.sha256(json.dumps(data).encode()).hexdigest()


def selection_for(db, user_id):
    row = db.scalar(select(m.AIConnection).where(m.AIConnection.user_id == user_id).execution_options(populate_existing=True))
    if row is None:
        return Selection(user_id, 'local' if get_settings().ai_mode == 'http' else 'disabled', None,
                         model_id=ai.MODEL if get_settings().ai_mode == 'http' else None)
    return Selection(user_id, row.mode, row.revision, row.provider, row.base_url, row.model_id, row.encrypted_key)


def check_revision(selection, expected):
    if selection.revision != (str(expected) if expected is not None else None):
        fail(409, 'ai_connection_changed', 'AI connection changed. Refresh Settings and review the selected destination. No message was saved.')


def require_usable(selection):
    if selection.mode == 'external' and (not external_available() or not selection.encrypted_key):
        fail(503, 'ai_setup_required', 'User-provider AI is not available. Ask the operator to finish secure setup.')
    if selection.mode == 'local' and get_settings().ai_mode != 'http':
        fail(503, 'ai_unavailable', ai.UNAVAILABLE_MESSAGE)


def view(db, user):
    selected = selection_for(db, user.id)
    row = db.get(m.AIConnection, user.id)
    return {'mode': selected.mode, 'provider': selected.provider, 'base_url': selected.base_url,
            'model_id': selected.model_id, 'revision': selected.revision, 'has_key': bool(selected.encrypted_key),
            'test_status': row.test_status if row else 'untested',
            'tested_at': json_value(row.tested_at) if row else None, 'test_error': row.test_error if row else None,
            'local_available': get_settings().ai_mode == 'http',
            'external_available': external_available() and not user.is_demo,
            'custom_enabled': bool(get_settings().ai_allowed_base_urls.strip()),
            'consent_saved': user.ai_consent,
            'requests_per_minute': get_settings().ai_requests_per_minute,
            'requests_per_day': get_settings().ai_requests_per_day}


def mutation_user(request: Request, user=Depends(current_user), db=Depends(get_db), credentials=Depends(bearer)):
    # Refresh cookies stay scoped to /auth. Bind CSRF to the signed bearer session, after locking its owner.
    owner = ai_limits.lock_owner(db, user.id)
    session = access_session(credentials, db)
    if session.user_id != owner.id or not secrets.compare_digest(session.csrf_hash, digest(csrf_token(request))):
        fail(403, 'csrf_failed', 'Session owner changed. Sign in again before updating AI settings.')
    return owner


@router.get('')
def get_connection(user=Depends(current_user), db=Depends(get_db)):
    return view(db, user)


def replace(db, user, data):
    previous = selection_for(db, user.id)
    check_revision(previous, data.expected_revision)
    key = None
    provider = base = model = None
    if data.mode == 'external':
        if user.is_demo:
            fail(403, 'ai_account_required', 'Create a personal account to save a private API key. Do not put credentials in a disposable demo.')
        if not external_available():
            fail(503, 'ai_setup_required', 'The operator must enable user-provider AI and configure its dedicated encryption key.')
        try:
            base = external_ai.approved_base(data.provider, data.base_url)
        except ValueError:
            fail(422, 'ai_endpoint_rejected', 'Choose OpenAI or an exact operator-approved HTTPS base URL on port 443.')
        provider, model = data.provider, data.model_id
        if not model:
            fail(422, 'ai_model_required', 'Enter the model ID supported by your provider.')
        if data.api_key is not None:
            key = data.api_key.get_secret_value()
        elif previous.mode == 'external' and previous.provider == provider and previous.base_url == base:
            key = decrypt_key(previous)
        else:
            fail(422, 'ai_key_required', 'A new provider or destination requires a newly supplied API key.')
    elif data.mode == 'local':
        if get_settings().ai_mode != 'http':
            fail(422, 'ai_local_unavailable', 'The private Barakah checkpoint is not configured on this server.')
        model = ai.MODEL
    if data.mode != 'external' and any(value is not None for value in (data.api_key, data.provider, data.base_url, data.model_id)):
        fail(422, 'ai_connection_fields', 'Disabled and local modes do not accept external credentials or endpoint fields.')
    row = db.get(m.AIConnection, user.id)
    if row is None:
        row = m.AIConnection(user_id=user.id)
        db.add(row)
    row.revision = m.uid()  # Random generation prevents delete/recreate ABA, even across cleared connections.
    row.mode, row.provider, row.base_url, row.model_id = data.mode, provider, base, model
    row.encrypted_key = encrypt_key(key, user.id, provider, base, row.revision) if key else None
    row.test_status, row.tested_at, row.test_error = 'untested', None, None
    user.ai_consent = False
    user.ai_consent_version += 1
    db.flush()
    return {**view(db, user), 'user': user_view(user)}


@router.put('')
def save_connection(data: s.AIConnectionUpdate, user=Depends(mutation_user), db=Depends(get_db)):
    return replace(db, user, data)


@router.delete('')
def remove_connection(data: s.AIConnectionVersion, user=Depends(mutation_user), db=Depends(get_db)):
    return replace(db, user, s.AIConnectionUpdate(mode='disabled', expected_revision=data.expected_revision))


def generate(request, selected):
    if selected.mode == 'local':
        return ai.send_message(request)
    if selected.mode == 'external':
        require_usable(selected)
        return external_ai.send(request, selected, decrypt_key(selected))
    return ai.AIResult(request.conversation_id)


def revalidate(db, selected, credentials, profile_version, consent_version, lease):
    if db.bind.dialect.name == 'sqlite':
        db.execute(text('BEGIN IMMEDIATE'))
    db.expire_all()
    owner = ai_limits.lock_owner(db, selected.user_id)
    current_user(credentials, db)
    if not owner.ai_consent or owner.updated_at != profile_version or owner.ai_consent_version != consent_version:
        fail(409, 'ai_consent_changed', 'Settings changed during generation. No message was saved.')
    check_revision(selection_for(db, owner.id), selected.revision)
    require_usable(selected)
    usage = ai_limits.check_lease(db, owner.id, lease)
    return owner, usage


@router.post('/test')
def test_connection(data: s.AIConnectionVersion, user=Depends(mutation_user), db=Depends(get_db), credentials=Depends(bearer)):
    selected = selection_for(db, user.id)
    check_revision(selected, data.expected_revision)
    require_usable(selected)
    if selected.mode == 'disabled':
        fail(503, 'ai_unavailable', ai.UNAVAILABLE_MESSAGE)
    if not user.ai_consent:
        fail(403, 'ai_consent_required', 'Save AI consent in Settings before testing. The test sends a fixed synthetic question and may incur a small charge.')
    profile_version, consent_version = user.updated_at, user.ai_consent_version
    duration = get_settings().ai_timeout_seconds if selected.mode == 'local' else get_settings().external_ai_timeout_seconds
    lease = ai_limits.reserve(db, user.id, duration)
    user_id = user.id
    try:
        result = generate(ai.AIRequest('Reply briefly with OK. This is a synthetic connection test.'), selected)
        owner, usage = revalidate(db, selected, credentials, profile_version, consent_version, lease)
        row = db.get(m.AIConnection, owner.id)
        if row is None:
            # Materialize the inherited local selection only after revalidation; preserve consent and destination.
            row = m.AIConnection(user_id=owner.id, mode=selected.mode, model_id=selected.model_id)
            db.add(row)
        row.test_status = 'failed' if result.error else 'success'
        row.test_error = result.error.code if result.error else None
        row.tested_at = ai_limits.clock(db)
        usage.lease_token = usage.lease_until = None
        db.commit()
        if result.error:
            fail(504 if result.error.code == 'ai_timeout' else 503, result.error.code, result.error.message)
        return {'status': 'success', 'connection_revision': row.revision,
                'message': 'The saved provider/model returned a valid reply. This is not a quality or safety certification.'}
    finally:
        ai_limits.release(db, user_id, lease)
