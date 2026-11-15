from datetime import date
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from . import models as m, schemas as s
from .db import get_db
from .security import current_user, admin_user
from .common import cents, fail, owned, pagination, public, rows
from .calculations import zakat_estimate

router = APIRouter(tags=['zakat and giving'])


def profile_row(db, user_id):
    result = db.scalar(select(m.ZakatProfile).where(m.ZakatProfile.user_id == user_id))
    if result is None:
        fail(404, 'not_found', 'Save a zakat profile first')
    return result


@router.get('/zakat/profile')
def get_profile(user=Depends(current_user), db=Depends(get_db)):
    return profile_row(db, user.id).data


@router.put('/zakat/profile')
def put_profile(data: s.ZakatProfileInput, user=Depends(current_user), db=Depends(get_db)):
    # Lock owner to serialize creation of the single per-user profile on PostgreSQL.
    db.scalar(select(m.User).where(m.User.id == user.id).with_for_update())
    row = db.scalar(select(m.ZakatProfile).where(m.ZakatProfile.user_id == user.id))
    if row is None:
        row = m.ZakatProfile(user_id=user.id)
        db.add(row)
    row.data = data.model_dump(mode='json')
    db.flush()
    return row.data


@router.get('/zakat/estimate')
def estimate(user=Depends(current_user), db=Depends(get_db)):
    return zakat_estimate(profile_row(db, user.id).data)


def history_view(db, history):
    paid = sum((p.amount for p in db.scalars(select(m.Giving).where(m.Giving.user_id == history.user_id, m.Giving.history_id == history.id, m.Giving.kind == 'zakat'))), Decimal(0))
    return {**public(history), 'paid_amount': str(cents(paid)), 'remaining_amount': str(cents(max(Decimal(0), Decimal(history.estimate['estimated_due']) - paid)))}


@router.post('/zakat/history', status_code=201)
def create_history(user=Depends(current_user), db=Depends(get_db)):
    profile = profile_row(db, user.id).data
    history = m.ZakatHistory(user_id=user.id, profile=profile, estimate=zakat_estimate(profile))
    db.add(history)
    db.flush()
    return history_view(db, history)


@router.get('/zakat/history')
def history(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [history_view(db, item) for item in rows(db, m.ZakatHistory, user.id, page)]


@router.post('/zakat/payments', status_code=201)
def create_payment(data: s.ZakatPaymentCreate, user=Depends(current_user), db=Depends(get_db)):
    if data.history_id:
        history = owned(db, m.ZakatHistory, data.history_id, user.id)
        if history.estimate['currency'] != data.currency:
            fail(422, 'currency_mismatch', 'Payment and snapshot currencies must match')
    payment = m.Giving(user_id=user.id, kind='zakat', **data.model_dump(exclude={'history_id'}), history_id=str(data.history_id) if data.history_id else None)
    db.add(payment)
    db.flush()
    return {**public(payment), 'payment_processed': False}


@router.patch('/zakat/payments/{payment_id}')
def update_payment(payment_id: UUID, data: s.ZakatPaymentCreate, user=Depends(current_user), db=Depends(get_db)):
    payment = owned(db, m.Giving, payment_id, user.id, lock=True)
    if payment.kind != 'zakat':
        fail(404, 'not_found', 'Zakat payment not found')
    if data.history_id:
        history = owned(db, m.ZakatHistory, data.history_id, user.id)
        if history.estimate['currency'] != data.currency:
            fail(422, 'currency_mismatch', 'Payment and snapshot currencies must match')
    for key, value in data.model_dump(exclude={'history_id'}).items():
        setattr(payment, key, value)
    payment.history_id = str(data.history_id) if data.history_id else None
    db.flush()
    return {**public(payment), 'payment_processed': False}


@router.delete('/zakat/payments/{payment_id}', status_code=204)
def delete_payment(payment_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    payment = owned(db, m.Giving, payment_id, user.id, lock=True)
    if payment.kind != 'zakat':
        fail(404, 'not_found', 'Zakat payment not found')
    db.delete(payment)


@router.get('/zakat/payments')
def payments(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [{**public(item), 'payment_processed': False} for item in rows(db, m.Giving, user.id, page, m.Giving.kind == 'zakat')]


@router.get('/causes')
def causes(category: str | None = Query(None, max_length=80), query: str | None = Query(None, max_length=100), page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    statement = select(m.Cause)
    if category and category != 'All':
        statement = statement.where(m.Cause.category == category)
    if query:
        statement = statement.where(m.Cause.title.icontains(query, autoescape=True))
    return [public(cause) for cause in db.scalars(statement.order_by(m.Cause.id).limit(page[0]).offset(page[1]))]


@router.post('/admin/causes', status_code=201)
def create_cause(data: s.CauseCreate, user=Depends(admin_user), db=Depends(get_db)):
    cause = m.Cause(**data.model_dump())
    db.add(cause)
    db.flush()
    return public(cause)


@router.post('/donation-intents', status_code=201)
def create_intent(data: s.DonationCreate, user=Depends(current_user), db=Depends(get_db)):
    cause = db.get(m.Cause, str(data.cause_id))
    if cause is None:
        fail(404, 'not_found', 'Cause not found')
    if cause.currency != data.currency:
        fail(422, 'currency_mismatch', 'Intention currency must match cause')
    intent = m.DonationIntent(user_id=user.id, cause_id=cause.id, currency=data.currency, amount=data.amount)
    db.add(intent)
    db.flush()
    return {**public(intent), 'status': 'recorded', 'payment_processed': False}


@router.get('/donation-intents')
def intents(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [{**public(item), 'status': 'recorded', 'payment_processed': False} for item in rows(db, m.DonationIntent, user.id, page)]


def giving_conditions(category, start_date, end_date):
    conditions = [m.Giving.kind == 'sadaqah']
    if category:
        conditions.append(m.Giving.category == category)
    if start_date:
        conditions.append(m.Giving.paid_on >= start_date)
    if end_date:
        conditions.append(m.Giving.paid_on <= end_date)
    if start_date and end_date and start_date > end_date:
        fail(422, 'validation_error', 'Date range is inverted')
    return conditions


@router.get('/sadaqah')
def sadaqah(category: str | None = Query(None, max_length=80), start_date: date | None = None, end_date: date | None = None, page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [public(item) for item in rows(db, m.Giving, user.id, page, *giving_conditions(category, start_date, end_date))]


@router.get('/sadaqah/summary')
def sadaqah_summary(category: str | None = Query(None, max_length=80), start_date: date | None = None, end_date: date | None = None, user=Depends(current_user), db=Depends(get_db)):
    from collections import defaultdict
    today = date.today()
    totals = defaultdict(lambda: {'total': Decimal(0), 'monthly_total': Decimal(0), 'annual_total': Decimal(0), 'donation_count': 0, 'by_recipient': defaultdict(Decimal), 'by_category': defaultdict(Decimal)})
    for item in db.scalars(select(m.Giving).where(m.Giving.user_id == user.id, *giving_conditions(category, start_date, end_date))):
        summary = totals[item.currency]
        summary['total'] += item.amount
        summary['donation_count'] += 1
        summary['by_recipient'][item.recipient] += item.amount
        summary['by_category'][item.category] += item.amount
        if item.paid_on.year == today.year:
            summary['annual_total'] += item.amount
            if item.paid_on.month == today.month:
                summary['monthly_total'] += item.amount
    result = []
    for currency, summary in sorted(totals.items()):
        item = {'currency': currency}
        for key, value in summary.items():
            if isinstance(value, dict):
                item[key] = {name: str(cents(amount)) for name, amount in value.items()}
            else:
                item[key] = str(cents(value)) if isinstance(value, Decimal) else value
        result.append(item)
    return result


@router.post('/sadaqah', status_code=201)
def create_sadaqah(data: s.GivingCreate, user=Depends(current_user), db=Depends(get_db)):
    item = m.Giving(user_id=user.id, kind='sadaqah', **data.model_dump())
    db.add(item)
    db.flush()
    return public(item)


@router.patch('/sadaqah/{giving_id}')
def update_sadaqah(giving_id: UUID, data: s.GivingCreate, user=Depends(current_user), db=Depends(get_db)):
    item = owned(db, m.Giving, giving_id, user.id, lock=True)
    if item.kind != 'sadaqah':
        fail(404, 'not_found', 'Giving record not found')
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    return public(item)


@router.delete('/sadaqah/{giving_id}', status_code=204)
def delete_sadaqah(giving_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    item = owned(db, m.Giving, giving_id, user.id)
    if item.kind != 'sadaqah':
        fail(404, 'not_found', 'Giving record not found')
    db.delete(item)


def goal_view(goal):
    return {**public(goal), 'remaining_amount': str(cents(max(Decimal(0), goal.target_amount - goal.saved_amount))),
            'progress_percent': str(cents(goal.saved_amount / goal.target_amount * 100))}


@router.get('/goals')
def goals(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [goal_view(item) for item in rows(db, m.Goal, user.id, page)]


@router.post('/goals', status_code=201)
def create_goal(data: s.GoalCreate, user=Depends(current_user), db=Depends(get_db)):
    goal = m.Goal(user_id=user.id, **data.model_dump())
    db.add(goal)
    db.flush()
    return goal_view(goal)


@router.patch('/goals/{goal_id}')
def update_goal(goal_id: UUID, data: s.GoalCreate, user=Depends(current_user), db=Depends(get_db)):
    goal = owned(db, m.Goal, goal_id, user.id, lock=True)
    if goal.saved_amount and data.currency != goal.currency:
        fail(409, 'currency_mismatch', 'Cannot change currency after contributions')
    for key, value in data.model_dump().items():
        setattr(goal, key, value)
    return goal_view(goal)


@router.post('/goals/{goal_id}/contributions', status_code=201)
def contribute(goal_id: UUID, data: s.ContributionCreate, user=Depends(current_user), db=Depends(get_db)):
    goal = owned(db, m.Goal, goal_id, user.id, lock=True)
    if goal.saved_amount + data.amount > Decimal('999999999999.99'):
        fail(409, 'balance_limit', 'Goal balance limit exceeded')
    goal.saved_amount += data.amount
    contribution = m.Contribution(user_id=user.id, goal_id=goal.id, amount=data.amount)
    db.add(contribution)
    db.flush()
    return public(contribution)


def contribution_for_goal(db, goal_id, contribution_id, user_id):
    goal = owned(db, m.Goal, goal_id, user_id, lock=True)
    item = owned(db, m.Contribution, contribution_id, user_id, lock=True)
    if item.goal_id != goal.id:
        fail(404, 'not_found', 'Contribution not found for this goal')
    return goal, item


@router.patch('/goals/{goal_id}/contributions/{contribution_id}')
def update_contribution(goal_id: UUID, contribution_id: UUID, data: s.ContributionCreate, user=Depends(current_user), db=Depends(get_db)):
    goal, item = contribution_for_goal(db, goal_id, contribution_id, user.id)
    revised = goal.saved_amount - item.amount + data.amount
    if revised > Decimal('999999999999.99'):
        fail(409, 'balance_limit', 'Goal balance limit exceeded')
    goal.saved_amount, item.amount = revised, data.amount
    db.flush()
    return public(item)


@router.delete('/goals/{goal_id}/contributions/{contribution_id}', status_code=204)
def delete_contribution(goal_id: UUID, contribution_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    goal, item = contribution_for_goal(db, goal_id, contribution_id, user.id)
    goal.saved_amount -= item.amount
    db.delete(item)


@router.get('/goals/{goal_id}/contributions')
def contributions(goal_id: UUID, page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    owned(db, m.Goal, goal_id, user.id)
    return [public(item) for item in rows(db, m.Contribution, user.id, page, m.Contribution.goal_id == str(goal_id))]


@router.delete('/goals/{goal_id}', status_code=204)
def delete_goal(goal_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    db.delete(owned(db, m.Goal, goal_id, user.id, lock=True))
