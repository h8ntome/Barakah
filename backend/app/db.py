import os
from decimal import Decimal
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine, event, text, Numeric, String
from sqlalchemy.types import TypeDecorator
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import get_settings


class ExactDecimal(TypeDecorator):
    """SQLite stores Decimal as text to avoid binary-float loss; PostgreSQL uses NUMERIC."""
    impl = Numeric(24, 6)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(String(40) if dialect.name == 'sqlite' else Numeric(24, 6))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return format(value, 'f') if dialect.name == 'sqlite' else value

    def process_result_value(self, value, dialect):
        return Decimal(value) if value is not None else None


class Base(DeclarativeBase):
    pass


def make_engine(url):
    options = {}
    if os.environ.get('VERCEL') == '1' and url.startswith('postgresql+psycopg://'):
        # The hosted pooler owns connections; suspended functions must not hoard them.
        options = {'poolclass': NullPool, 'connect_args': {'prepare_threshold': None}}
    elif url.startswith('sqlite'):
        options = {'connect_args': {'check_same_thread': False, 'timeout': 30}}
    engine = create_engine(url, pool_pre_ping=True, hide_parameters=True, **options)
    if url.startswith('sqlite'):
        @event.listens_for(engine, 'connect')
        def configure_sqlite(connection, _):
            connection.execute('PRAGMA foreign_keys=ON')
    return engine


engine = make_engine(get_settings().database_url)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db():
    with SessionLocal() as db:
        try:
            # SQLite lacks row locks: serialize transactions before reading balances/sessions.
            if db.bind.dialect.name == 'sqlite':
                db.execute(text('BEGIN IMMEDIATE'))
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
