from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, or_
from . import models as m, schemas as s
from .db import get_db
from .security import current_user, admin_user, limiter
from .common import fail, pagination, public

router = APIRouter(tags=['contextual ads'])


def available_ads():
    today = datetime.now(timezone.utc).date()
    return [m.Ad.active.is_(True), m.Ad.approved.is_(True), or_(m.Ad.starts_on.is_(None), m.Ad.starts_on <= today), or_(m.Ad.ends_on.is_(None), m.Ad.ends_on >= today)]


@router.get('/ads')
def ads(context: Literal['dashboard', 'giving', 'education'], page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    items = db.scalars(select(m.Ad).where(*available_ads(), m.Ad.context == context).order_by(m.Ad.id).limit(page[0]).offset(page[1]))
    return [{**public(item, exclude={'approved', 'active'}), 'sponsored': True} for item in items]


@router.post('/ads/{ad_id}/events', status_code=201)
def event(ad_id: UUID, data: s.AdEventCreate, user=Depends(current_user), db=Depends(get_db)):
    limiter.check(('ads', user.id), 120)
    ad = db.scalar(select(m.Ad).where(m.Ad.id == str(ad_id), *available_ads()))
    if ad is None:
        fail(404, 'not_found', 'Advertisement not available')
    event = m.AdEvent(user_id=user.id, ad_id=ad.id, kind=data.kind)
    db.add(event)
    db.flush()
    return public(event)


@router.get('/admin/ads')
def admin_ads(page=Depends(pagination), user=Depends(admin_user), db=Depends(get_db)):
    return [public(item) for item in db.scalars(select(m.Ad).order_by(m.Ad.id).limit(page[0]).offset(page[1]))]


@router.post('/admin/ads', status_code=201)
def create_ad(data: s.AdCreate, user=Depends(admin_user), db=Depends(get_db)):
    ad = m.Ad(**data.model_dump())
    db.add(ad)
    db.flush()
    return public(ad)


@router.patch('/admin/ads/{ad_id}')
def update_ad(ad_id: UUID, data: s.AdUpdate, user=Depends(admin_user), db=Depends(get_db)):
    ad = db.scalar(select(m.Ad).where(m.Ad.id == str(ad_id)).with_for_update())
    if ad is None:
        fail(404, 'not_found', 'Advertisement not found')
    fields = data.model_dump(exclude_unset=True)
    for key, value in fields.items():
        if value is None and key not in {'starts_on', 'ends_on'}:
            fail(422, 'validation_error', 'Only campaign dates may be null')
        setattr(ad, key, value)
    if ad.starts_on and ad.ends_on and ad.starts_on > ad.ends_on:
        fail(422, 'validation_error', 'Campaign end precedes start')
    return public(ad)


@router.get('/admin/ad-events')
def ad_events(page=Depends(pagination), user=Depends(admin_user), db=Depends(get_db)):
    results = db.execute(select(m.AdEvent.ad_id, m.AdEvent.kind, func.count(m.AdEvent.id)).group_by(m.AdEvent.ad_id, m.AdEvent.kind).order_by(m.AdEvent.ad_id, m.AdEvent.kind).limit(page[0]).offset(page[1])).all()
    return [{'ad_id': ad_id, 'kind': kind, 'count': count} for ad_id, kind, count in results]
