import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select, update
from . import schemas as s
from .models import User, PasswordReset
from .db import get_db
from .security import auth_limit, current_user, digest, dummy_hash, hasher, issue_session, clear_cookies, refresh_session, revoke_sessions, user_view, utc, verify_password
from .config import get_settings
from .common import fail
from .mail import send_reset_email

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', status_code=201, dependencies=[Depends(auth_limit)])
def register(data: s.Register, response: Response, db=Depends(get_db)):
    email = str(data.email).lower()
    if db.scalar(select(User).where(User.email == email)):
        fail(409, 'registration_failed', 'This email is already registered. Sign in or reset your password.')
    user = User(email=email, display_name=data.display_name, password_hash=hasher.hash(data.password))
    db.add(user)
    db.flush()
    return issue_session(db, user, response)


@router.post('/login', dependencies=[Depends(auth_limit)])
def login(data: s.Login, response: Response, db=Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()).with_for_update())
    valid = verify_password(data.password, user.password_hash if user else dummy_hash)
    if not user or not valid or user.is_demo:
        fail(401, 'invalid_credentials', 'Invalid email or password')
    return issue_session(db, user, response)


@router.post('/refresh', dependencies=[Depends(auth_limit)])
def refresh(request: Request, response: Response, db=Depends(get_db)):
    session = refresh_session(request, db)
    session.revoked = True
    return issue_session(db, db.get(User, session.user_id), response)


@router.post('/logout', status_code=204)
def logout(request: Request, response: Response, db=Depends(get_db)):
    refresh_session(request, db).revoked = True
    clear_cookies(response)


@router.get('/me')
def me(user=Depends(current_user)):
    return user_view(user)


@router.patch('/profile')
def profile(data: s.ProfileUpdate, user=Depends(current_user), db=Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if data.ai_consent is not None and data.ai_consent != user.ai_consent:
        user.ai_consent_version += 1
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    db.flush()
    return user_view(user)


@router.post('/password', status_code=204, dependencies=[Depends(auth_limit)])
def password(data: s.PasswordChange, response: Response, user=Depends(current_user), db=Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if not user or not verify_password(data.current_password, user.password_hash):
        fail(401, 'invalid_credentials', 'Invalid password')
    user.password_hash = hasher.hash(data.new_password)
    revoke_sessions(db, user.id)
    db.execute(update(PasswordReset).where(PasswordReset.user_id == user.id).values(used=True))
    clear_cookies(response)


@router.post('/reset/request', dependencies=[Depends(auth_limit)])
def reset_request(data: s.ResetRequest, db=Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(data.email).lower()).with_for_update())
    config = get_settings()
    if not config.reset_outbox and not config.smtp_host:
        fail(503, 'reset_unavailable', 'Password reset delivery is not configured')
    if user and not user.is_demo:
        token = secrets.token_urlsafe(48)
        db.execute(update(PasswordReset).where(PasswordReset.user_id == user.id).values(used=True))
        db.add(PasswordReset(user_id=user.id, token_hash=digest(token), expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)))
        if config.reset_outbox:
            directory = Path(config.reset_outbox)
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            path = directory / (secrets.token_hex(16) + '.json')
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as output:
                json.dump({'email': user.email, 'token': token}, output)
        else:
            send_reset_email(user.email, token)
    return {'message': 'If the address is registered and reset delivery is configured, reset instructions will be sent.'}


@router.post('/reset/confirm', status_code=204, dependencies=[Depends(auth_limit)])
def reset_confirm(data: s.ResetConfirm, response: Response, db=Depends(get_db)):
    reset = db.scalar(select(PasswordReset).where(PasswordReset.token_hash == digest(data.token)))
    if reset:
        db.scalar(select(User).where(User.id == reset.user_id).with_for_update())
        reset = db.scalar(select(PasswordReset).where(PasswordReset.id == reset.id).with_for_update().execution_options(populate_existing=True))
    if not reset or reset.used or utc(reset.expires_at) <= datetime.now(timezone.utc):
        fail(400, 'invalid_reset', 'Invalid or expired reset token')
    user = db.get(User, reset.user_id)
    user.password_hash = hasher.hash(data.new_password)
    db.execute(update(PasswordReset).where(PasswordReset.user_id == user.id).values(used=True))
    revoke_sessions(db, user.id)
    clear_cookies(response)


@router.delete('/me', status_code=204, dependencies=[Depends(auth_limit)])
def delete_me(data: s.DeleteUser, response: Response, user=Depends(current_user), db=Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if not user or not verify_password(data.password, user.password_hash):
        fail(401, 'invalid_credentials', 'Invalid password')
    db.delete(user)
    db.flush()
    clear_cookies(response)
