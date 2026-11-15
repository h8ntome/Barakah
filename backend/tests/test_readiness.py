from sqlalchemy.exc import OperationalError


def test_readiness_uses_migrated_database(client):
    assert client.get('/health').json() == {'status': 'ok'}
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json()['database'] == 'available'


def test_readiness_rejects_older_migration(client, db_setup):
    from sqlalchemy import text
    with db_setup.begin() as session:
        session.execute(text("UPDATE alembic_version SET version_num = '2725283e7c2a'"))
    response = client.get('/api/v1/health')
    assert response.status_code == 503
    assert response.json()['database'] == 'migration_required'


def test_database_failure_is_not_reported_healthy(client, monkeypatch):
    from app import db
    def unavailable():
        raise OperationalError('private database address', {}, Exception('private connection error'))
    monkeypatch.setattr(db, 'SessionLocal', unavailable)
    response = client.get('/api/v1/health')
    assert response.status_code == 503
    assert 'private' not in response.text
    assert client.get('/health').status_code == 200
