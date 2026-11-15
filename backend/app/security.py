import hashlib
import secrets
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from .config import get_settings
from .db import get_db
from .models import User, Session
from .common import fail

hasher = PasswordHasher()
dummy_hash = hasher.hash('constant-dummy-password-no-user')
bearer = HTTPBearer(auto_error=False)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def verify_password(value, hashed):
    try:
        return hasher.verify(hashed, value)
    except (VerificationError, InvalidHashError):
        return False


def utc(value):
    return value.replace(tzinfo=value.tzinfo or timezone.utc)


class RateLimiter:
    def __init__(self):
        self.entries = OrderedDict()
        self.lock = threading.Lock()

    def check(self, key, limit):
        current = time.monotonic()
        with self.lock:
            while self.entries and next(iter(self.entries.values()))[0] < current - 60:
                self.entries.popitem(last=False)
            start, count = self.entries.get(key, (current, 0))
            if current - start >= 60:
                start, count = current, 0
            if count >= limit:
                fail(429, 'rate_limited', 'Too many requests; retry in one minute')
            if key not in self.entries and len(self.entries) >= 10000:
                fail(429, 'rate_limited', 'Service busy; retry in one minute')
            self.entries[key] = (start, count + 1)


limiter = RateLimiter()


def auth_limit(request: Request):
    # Never trust arbitrary forwarded headers; configure proxy/edge limits separately.
    limiter.check(('auth', request.client.host if request.client else 'unknown'), get_settings().auth_rate_limit)


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db=Depends(get_db)):
    if credentials is None:
        fail(401, 'unauthorized', 'Authentication required')
    try:
        payload = jwt.decode(credentials.credentials, get_settings().secret_key, algorithms=['HS256'], audience='barakah', issuer='barakah-api', options={'require': ['exp', 'iat', 'sub', 'sid', 'aud', 'iss']})
        session = db.scalar(select(Session).where(Session.id == payload['sid'], Session.user_id == payload['sub']))
        if not session or session.revoked or utc(session.expires_at) <= datetime.now(timezone.utc):
            fail(401, 'unauthorized', 'Session expired or revoked')
        user = db.get(User, session.user_id)
        if user is None:
            fail(401, 'unauthorized', 'Authentication required')
        return user
    except jwt.InvalidTokenError:
        fail(401, 'unauthorized', 'Invalid or expired access token')


def admin_user(user=Depends(current_user)):
    if not user.is_admin:
        fail(403, 'forbidden', 'Administrator access required')
    return user


def user_view(user):
    return {key: getattr(user, key) for key in ('id', 'email', 'display_name', 'ai_consent', 'is_admin', 'country', 'timezone', 'language', 'currency')}


def issue_session(db, user, response):
    config = get_settings()
    refresh, csrf = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    session = Session(user_id=user.id, token_hash=digest(refresh), csrf_hash=digest(csrf), expires_at=now + timedelta(days=30))
    db.add(session)
    db.flush()
    access = jwt.encode({'sub': user.id, 'sid': session.id, 'iat': now, 'exp': now + timedelta(minutes=15), 'aud': 'barakah', 'iss': 'barakah-api'}, config.secret_key, algorithm='HS256')
    response.set_cookie('refresh_token', refresh, max_age=30 * 86400, httponly=True, secure=config.cookie_secure, samesite='lax', path='/api/v1/auth')
    response.set_cookie('csrf_token', csrf, max_age=30 * 86400, httponly=False, secure=config.cookie_secure, samesite='lax', path='/')
    return {'access_token': access, 'token_type': 'bearer', 'user': user_view(user)}


def clear_cookies(response):
    response.delete_cookie('refresh_token', path='/api/v1/auth', secure=get_settings().cookie_secure, httponly=True, samesite='lax')
    response.delete_cookie('csrf_token', path='/', secure=get_settings().cookie_secure, samesite='lax')


def refresh_session(request, db):
    if request.headers.get('origin') not in get_settings().origins:
        fail(403, 'csrf_failed', 'Trusted Origin required')
    csrf = request.headers.get('x-csrf-token', '')
    cookie = request.cookies.get('csrf_token', '')
    if not csrf or not cookie or not secrets.compare_digest(csrf, cookie):
        fail(403, 'csrf_failed', 'CSRF token required')
    refresh = request.cookies.get('refresh_token', '')
    session = db.scalar(select(Session).where(Session.token_hash == digest(refresh)))
    if session:
        # All credential mutations lock owner before session/reset rows.
        db.scalar(select(User).where(User.id == session.user_id).with_for_update())
        session = db.scalar(select(Session).where(Session.id == session.id).with_for_update().execution_options(populate_existing=True))
    if not session or session.revoked or utc(session.expires_at) <= datetime.now(timezone.utc):
        fail(401, 'unauthorized', 'Invalid refresh session')
    if not secrets.compare_digest(session.csrf_hash, digest(csrf)):
        fail(403, 'csrf_failed', 'Invalid CSRF token')
    return session


def revoke_sessions(db, user_id):
    db.execute(update(Session).where(Session.user_id == user_id).values(revoked=True))
