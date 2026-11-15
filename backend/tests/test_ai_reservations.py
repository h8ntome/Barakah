"""Independent spawned workers, separate engines, one shared SQLite/PostgreSQL database."""
import multiprocessing
import time
import pytest
from fastapi import HTTPException
from sqlalchemy import select, text, func
from sqlalchemy.orm import Session
from app import ai_limits, models as m
from app.config import get_settings
from app.db import make_engine


def reserve_worker(url, owner_id, ready, start, results, limits, release):
    engine = None
    try:
        for name, value in limits.items(): setattr(get_settings(), name, value)
        engine = make_engine(url)
        ready.put(True)
        if not start.wait(10): raise RuntimeError('Start barrier timed out')
        with Session(engine) as db:
            try:
                if engine.dialect.name == 'sqlite': db.execute(text('BEGIN IMMEDIATE'))
                ai_limits.lock_owner(db, owner_id)
                token = ai_limits.reserve(db, owner_id, 35)
                if release: ai_limits.release(db, owner_id, token)
                results.put(('ok', owner_id))
            except HTTPException as error:
                db.rollback()
                results.put(('rejected', error.detail['code']))
    except BaseException as error:
        results.put(('error', type(error).__name__))
    finally:
        if engine: engine.dispose()


@pytest.mark.parametrize('case', ['same_owner', 'global_capacity', 'daily_quota'])
def test_concurrent_reservations_across_processes(db_setup, case):
    with db_setup.begin() as db:
        owners = [m.User(email=f'reserve-{index}@example.com', display_name='Quota fixture', password_hash='unusable-test-hash') for index in range(4)]
        db.add_all(owners); db.flush()
        ids = [owner.id for owner in owners]
    url = db_setup.kw['bind'].url.render_as_string(hide_password=False)
    ctx = multiprocessing.get_context('spawn')
    ready, results, start = ctx.Queue(), ctx.Queue(), ctx.Event()
    limits = {'ai_global_inflight_limit': 2, 'ai_requests_per_minute': 60, 'ai_requests_per_day': 1 if case == 'daily_quota' else 30}
    workers = [ctx.Process(target=reserve_worker, args=(url, ids[i] if case == 'global_capacity' else ids[0],
        ready, start, results, limits, case == 'daily_quota')) for i in range(4)]
    try:
        for worker in workers: worker.start()
        for _ in workers: assert ready.get(timeout=15)
        started = time.monotonic(); start.set()
        outcomes = [results.get(timeout=10) for _ in workers]
        assert time.monotonic() - started < 8
        assert sum(result[0] == 'ok' for result in outcomes) == (2 if case == 'global_capacity' else 1), outcomes
        # A contender can arrive before the successful worker releases its lease.
        allowed = {'ai_busy', 'ai_quota_reached'} if case == 'daily_quota' else {'ai_busy'}
        assert all(result[0] == 'ok' or result[0] == 'rejected' and result[1] in allowed for result in outcomes), outcomes
        with db_setup() as db:
            assert db.scalar(select(func.sum(m.AIUsage.day_count))) == (2 if case == 'global_capacity' else 1)
            assert db.scalar(select(func.count()).select_from(m.AIUsage).where(m.AIUsage.lease_token.is_not(None))) == (0 if case == 'daily_quota' else 2 if case == 'global_capacity' else 1)
        if case == 'daily_quota':
            with db_setup() as db:
                if db.bind.dialect.name == 'sqlite': db.execute(text('BEGIN IMMEDIATE'))
                ai_limits.lock_owner(db, ids[0])
                config = get_settings()
                original = config.ai_requests_per_day
                try:
                    config.ai_requests_per_day = 1
                    with pytest.raises(HTTPException) as caught: ai_limits.reserve(db, ids[0], 35)
                    assert caught.value.detail['code'] == 'ai_quota_reached'
                finally:
                    config.ai_requests_per_day = original
        for worker in workers:
            worker.join(timeout=5)
            assert worker.exitcode == 0
    finally:
        start.set()
        for worker in workers:
            if worker.is_alive(): worker.terminate()
            worker.join(timeout=5)
        ready.close(); results.close()
