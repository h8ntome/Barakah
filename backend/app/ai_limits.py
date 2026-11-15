"""Database-backed admission: attempted calls, one lease per owner, bounded total concurrency."""
from datetime import timedelta
from sqlalchemy import select, func, text
from sqlalchemy.exc import SQLAlchemyError
from . import models as m
from .common import fail
from .config import get_settings
from .security import utc


def transaction_limits(db):
    if db.bind.dialect.name == 'postgresql':
        db.execute(text("SET LOCAL lock_timeout = '2s'"))
        db.execute(text("SET LOCAL statement_timeout = '3s'"))


def clock(db):
    return utc(db.scalar(select(func.current_timestamp())))


def lock_owner(db, user_id):
    transaction_limits(db)
    owner = db.scalar(select(m.User).where(m.User.id == user_id).with_for_update().execution_options(populate_existing=True))
    if owner is None:
        fail(401, 'unauthorized', 'Account no longer available. No message was saved.')
    return owner


def reserve(db, user_id, duration):
    # Caller holds the owner row. The singleton gate serializes the global capacity check.
    if db.scalar(select(m.AIGate).where(m.AIGate.id == 1).with_for_update()) is None:
        fail(503, 'ai_setup_required', 'AI capacity control is unavailable. Contact the operator.')
    now = clock(db)
    usage = db.get(m.AIUsage, user_id)
    if usage is None:
        usage = m.AIUsage(user_id=user_id, minute_start=now, day_start=now, minute_count=0, day_count=0)
        db.add(usage)
    if usage.lease_token and utc(usage.lease_until) > now:
        fail(429, 'ai_busy', 'An AI request is already in progress. Please wait before trying again.')
    active = db.scalar(select(func.count()).select_from(m.AIUsage).where(m.AIUsage.lease_until > now))
    config = get_settings()
    if active >= config.ai_global_inflight_limit:
        fail(429, 'ai_busy', 'AI capacity is currently full. Please try again later.')
    if now - utc(usage.minute_start) >= timedelta(minutes=1):
        usage.minute_start, usage.minute_count = now, 0
    if now - utc(usage.day_start) >= timedelta(days=1):
        usage.day_start, usage.day_count = now, 0
    if usage.minute_count >= config.ai_requests_per_minute or usage.day_count >= config.ai_requests_per_day:
        fail(429, 'ai_quota_reached', 'Your AI request allowance is exhausted. Tests and failed attempts also count.')
    token = m.uid()
    usage.minute_count += 1
    usage.day_count += 1
    usage.lease_token, usage.lease_until = token, now + timedelta(seconds=duration + 15)
    db.commit()  # Never hold DB locks during DNS or provider work; never refund ambiguous failures.
    return token


def check_lease(db, user_id, token):
    usage = db.scalar(select(m.AIUsage).where(m.AIUsage.user_id == user_id).execution_options(populate_existing=True))
    if not usage or usage.lease_token != token or utc(usage.lease_until) <= clock(db):
        fail(409, 'ai_request_expired', 'This AI request expired. No message was saved.')
    return usage


def release(db, user_id, token):
    # Failure cleanup is separate from message rollback. Never clear a replacement lease.
    db.rollback()
    try:
        if db.bind.dialect.name == 'sqlite':
            db.execute(text('BEGIN IMMEDIATE'))
        transaction_limits(db)
        owner = db.scalar(select(m.User).where(m.User.id == user_id).with_for_update())
        usage = db.get(m.AIUsage, user_id) if owner else None
        if usage and usage.lease_token == token:
            usage.lease_token = usage.lease_until = None
        db.commit()
    except SQLAlchemyError:
        db.rollback()  # Worker/DB failure is recovered by lease expiry; do not mask the original outcome.
