import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Text, Boolean, DateTime, Date, ForeignKey, Numeric, JSON, UniqueConstraint, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base, ExactDecimal


def uid():
    return str(uuid.uuid4())


def now():
    return datetime.now(timezone.utc)


class Identity:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)


class Owned(Identity):
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)


class User(Identity, Base):
    __tablename__ = 'users'
    # Legacy creation dates are unknown; new users always get UTC timestamps.
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    display_name: Mapped[str] = mapped_column(String(80))
    ai_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_consent_version: Mapped[int] = mapped_column(Integer, default=0, server_default='0')
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    demo_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    country: Mapped[str] = mapped_column(String(2), default='US')
    timezone: Mapped[str] = mapped_column(String(64), default='UTC')
    language: Mapped[str] = mapped_column(String(10), default='en')
    currency: Mapped[str] = mapped_column(String(3), default='USD')


class Session(Owned, Base):
    __tablename__ = 'sessions'
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    csrf_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class PasswordReset(Owned, Base):
    __tablename__ = 'password_resets'
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class Account(Owned, Base):
    __tablename__ = 'accounts'
    __table_args__ = (CheckConstraint('CAST(balance AS NUMERIC) >= 0', name='account_nonnegative'),)
    name: Mapped[str] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(3))
    account_type: Mapped[str] = mapped_column(String(20), default='cash')
    balance: Mapped[Decimal] = mapped_column(ExactDecimal(), default=0)


class Transaction(Owned, Base):
    __tablename__ = 'transactions'
    __table_args__ = (CheckConstraint('CAST(amount AS NUMERIC) > 0', name='transaction_positive'),)
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id', ondelete='CASCADE'), index=True)
    kind: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(ExactDecimal())
    currency: Mapped[str] = mapped_column(String(3))
    category: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(500), default='')
    occurred_on: Mapped[datetime] = mapped_column(Date)
    transfer_id: Mapped[str | None] = mapped_column(String(36))


class Budget(Owned, Base):
    __tablename__ = 'budgets'
    __table_args__ = (UniqueConstraint('user_id', 'category', 'currency', 'month', name='budget_unique'),)
    category: Mapped[str] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(3))
    amount: Mapped[Decimal] = mapped_column(ExactDecimal())
    month: Mapped[str] = mapped_column(String(7))


class ZakatProfile(Owned, Base):
    __tablename__ = 'zakat_profiles'
    __table_args__ = (UniqueConstraint('user_id', name='zakat_profile_user'),)
    data: Mapped[dict] = mapped_column(JSON)


class ZakatHistory(Owned, Base):
    __tablename__ = 'zakat_history'
    profile: Mapped[dict] = mapped_column(JSON)
    estimate: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Giving(Owned, Base):
    __tablename__ = 'giving'
    kind: Mapped[str] = mapped_column(String(16))
    amount: Mapped[Decimal] = mapped_column(ExactDecimal())
    currency: Mapped[str] = mapped_column(String(3))
    paid_on: Mapped[datetime] = mapped_column(Date)
    category: Mapped[str] = mapped_column(String(80), default='general')
    recipient: Mapped[str] = mapped_column(String(120))
    note: Mapped[str] = mapped_column(String(500), default='')
    history_id: Mapped[str | None] = mapped_column(ForeignKey('zakat_history.id', ondelete='SET NULL'))


class Cause(Identity, Base):
    __tablename__ = 'causes'
    title: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(1000))
    currency: Mapped[str] = mapped_column(String(3))


class DonationIntent(Owned, Base):
    __tablename__ = 'donation_intents'
    cause_id: Mapped[str] = mapped_column(ForeignKey('causes.id'))
    amount: Mapped[Decimal] = mapped_column(ExactDecimal())
    currency: Mapped[str] = mapped_column(String(3))


class Goal(Owned, Base):
    __tablename__ = 'goals'
    name: Mapped[str] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(3))
    target_amount: Mapped[Decimal] = mapped_column(ExactDecimal())
    saved_amount: Mapped[Decimal] = mapped_column(ExactDecimal(), default=0)
    target_date: Mapped[datetime | None] = mapped_column(Date)


class Contribution(Owned, Base):
    __tablename__ = 'contributions'
    goal_id: Mapped[str] = mapped_column(ForeignKey('goals.id', ondelete='CASCADE'))
    amount: Mapped[Decimal] = mapped_column(ExactDecimal())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Portfolio(Owned, Base):
    __tablename__ = 'portfolios'
    name: Mapped[str] = mapped_column(String(80))


class Holding(Owned, Base):
    __tablename__ = 'holdings'
    __table_args__ = (UniqueConstraint('user_id', 'portfolio_id', 'symbol', 'currency', name='holding_unique'), CheckConstraint('CAST(quantity AS NUMERIC) >= 0', name='holding_nonnegative'))
    portfolio_id: Mapped[str] = mapped_column(ForeignKey('portfolios.id', ondelete='CASCADE'))
    symbol: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(3))
    quantity: Mapped[Decimal] = mapped_column(ExactDecimal(), default=0)
    cost_basis: Mapped[Decimal] = mapped_column(ExactDecimal(), default=0)
    realized_gain: Mapped[Decimal] = mapped_column(ExactDecimal(), default=0)
    quote_price: Mapped[Decimal | None] = mapped_column(ExactDecimal())
    quote_date: Mapped[datetime | None] = mapped_column(Date)
    quote_source: Mapped[str | None] = mapped_column(String(200))
    screening_status: Mapped[str] = mapped_column(String(48), default='unverified')
    screening_source: Mapped[str | None] = mapped_column(String(200))
    screening_date: Mapped[datetime | None] = mapped_column(Date)
    screening_notes: Mapped[str | None] = mapped_column(String(1000))
    screening_assessment: Mapped[dict | None] = mapped_column(JSON)


class ScreeningRecord(Owned, Base):
    __tablename__ = 'screening_records'
    holding_id: Mapped[str] = mapped_column(ForeignKey('holdings.id', ondelete='CASCADE'), index=True)
    assessment: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Trade(Owned, Base):
    __tablename__ = 'trades'
    # Null ordering/snapshots identify legacy trades, which cannot be safely reversed.
    sequence: Mapped[int | None] = mapped_column(Integer)
    before_quantity: Mapped[Decimal | None] = mapped_column(ExactDecimal())
    before_cost_basis: Mapped[Decimal | None] = mapped_column(ExactDecimal())
    before_realized_gain: Mapped[Decimal | None] = mapped_column(ExactDecimal())
    holding_id: Mapped[str] = mapped_column(ForeignKey('holdings.id', ondelete='CASCADE'))
    side: Mapped[str] = mapped_column(String(4))
    quantity: Mapped[Decimal] = mapped_column(ExactDecimal())
    price: Mapped[Decimal] = mapped_column(ExactDecimal())
    fees: Mapped[Decimal] = mapped_column(ExactDecimal())
    realized_gain: Mapped[Decimal] = mapped_column(ExactDecimal(), default=0)
    traded_on: Mapped[datetime] = mapped_column(Date)


class AIConnection(Base):
    __tablename__ = 'ai_connections'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    mode: Mapped[str] = mapped_column(String(16), default='disabled')
    provider: Mapped[str | None] = mapped_column(String(24))
    base_url: Mapped[str | None] = mapped_column(String(500))
    model_id: Mapped[str | None] = mapped_column(String(160))
    encrypted_key: Mapped[str | None] = mapped_column(Text)
    revision: Mapped[str] = mapped_column(String(36), default=uid)
    test_status: Mapped[str] = mapped_column(String(16), default='untested')
    tested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    test_error: Mapped[str | None] = mapped_column(String(48))


class AIUsage(Base):
    __tablename__ = 'ai_usage'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    minute_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    minute_count: Mapped[int] = mapped_column(Integer, default=0)
    day_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    day_count: Mapped[int] = mapped_column(Integer, default=0)
    lease_token: Mapped[str | None] = mapped_column(String(36))
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class AIGate(Base):
    __tablename__ = 'ai_gate'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Conversation(Owned, Base):
    __tablename__ = 'conversations'
    connection_identity: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Message(Owned, Base):
    __tablename__ = 'messages'
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id', ondelete='CASCADE'))
    role: Mapped[str] = mapped_column(String(16))
    text: Mapped[str] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean)
    generation_metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Ad(Identity, Base):
    __tablename__ = 'ads'
    advertiser_name: Mapped[str] = mapped_column(String(120), default='', server_default='')
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000))
    context: Mapped[str] = mapped_column(String(20))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    starts_on: Mapped[datetime | None] = mapped_column(Date)
    ends_on: Mapped[datetime | None] = mapped_column(Date)


class AdEvent(Owned, Base):
    __tablename__ = 'ad_events'
    ad_id: Mapped[str] = mapped_column(ForeignKey('ads.id', ondelete='CASCADE'))
    kind: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
