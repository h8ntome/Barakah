from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, Query
from sqlalchemy import select


def fail(status, code, message):
    raise HTTPException(status, detail={'code': code, 'message': message})


def owned(db, model, resource_id, user_id, lock=False):
    query = select(model).where(model.id == str(resource_id), model.user_id == user_id)
    if lock:
        query = query.with_for_update()
    resource = db.scalar(query)
    if resource is None:
        fail(404, 'not_found', 'Resource not found')
    return resource


def pagination(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    return limit, offset


def rows(db, model, user_id, page, *conditions):
    return db.scalars(select(model).where(model.user_id == user_id, *conditions).order_by(model.id).limit(page[0]).offset(page[1])).all()


def cents(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def six(value):
    return Decimal(value).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


def json_value(value):
    if isinstance(value, Decimal):
        return format(value, 'f')
    if isinstance(value, datetime):
        return value.replace(tzinfo=value.tzinfo or timezone.utc).isoformat()
    if isinstance(value, dict):
        return {k: json_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_value(v) for v in value]
    return value


def public(resource, exclude=()):
    return {c.name: json_value(getattr(resource, c.name)) for c in resource.__table__.columns if c.name not in {'user_id', *exclude}}
