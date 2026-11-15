from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from app.config import get_settings
from app.db import make_engine
from app import mail


def test_smtp_starttls_message_no_response_token(client, auth, monkeypatch):
    events = []
    class SMTP:
        def __init__(self, host, port, timeout):
            events.append((host, port, timeout))
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def ehlo(self):
            events.append('ehlo')
        def starttls(self, context):
            assert context.check_hostname
            events.append('starttls')
        def login(self, username, password):
            events.append(('login', username, password))
        def send_message(self, message):
            events.append(message)
    monkeypatch.setattr(get_settings(), 'reset_outbox', None)
    monkeypatch.setattr(get_settings(), 'smtp_host', 'smtp.example.com')
    monkeypatch.setattr(get_settings(), 'smtp_username', 'server-user')
    monkeypatch.setattr(get_settings(), 'smtp_password', 'secret')
    monkeypatch.setattr(mail.smtplib, 'SMTP', SMTP)
    response = client.post('/api/v1/auth/reset/request', json={'email': 'one@example.com'})
    assert response.status_code == 200
    assert events[1:4] == ['ehlo', 'starttls', 'ehlo']
    assert 'token=' in events[-1].get_content()
    assert 'token=' not in response.text


def test_unconfigured_reset_is_explicit(client, monkeypatch):
    monkeypatch.setattr(get_settings(), 'reset_outbox', None)
    monkeypatch.setattr(get_settings(), 'smtp_host', None)
    response = client.post('/api/v1/auth/reset/request', json={'email': 'missing@example.com'})
    assert response.status_code == 503
    assert response.json()['error']['code'] == 'reset_unavailable'


def test_migration_upgrade_downgrade_round_trip(db_setup):
    config = Config(str(Path(__file__).parents[1] / 'alembic.ini'))
    command.check(config)
    command.downgrade(config, 'base')
    engine = make_engine(get_settings().database_url)
    assert 'users' not in inspect(engine).get_table_names()
    command.upgrade(config, 'head')
    command.check(config)
    assert {'users', 'accounts', 'transactions', 'holdings', 'portfolios', 'messages'}.issubset(inspect(engine).get_table_names())
    engine.dispose()
