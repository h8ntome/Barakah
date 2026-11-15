from collections import defaultdict
from datetime import date
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from . import models as m, schemas as s
from .db import get_db
from .security import current_user
from .common import cents, six, fail, json_value, owned, pagination, public, rows
from .calculations import apply_trade, screen

router = APIRouter(tags=['portfolio'])


def holding_view(holding):
    value = holding.quantity * holding.quote_price if holding.quote_price is not None else (Decimal(0) if not holding.quantity else None)
    snapshot = holding.screening_assessment
    stale = bool(snapshot and holding.screening_date and (date.today() - holding.screening_date).days > snapshot.get('max_age_days', 90))
    return {**public(holding), 'needs_reevaluation': stale, 'screening_status': 'uncertain' if stale else holding.screening_status, 'average_cost': str(six(holding.cost_basis / holding.quantity)) if holding.quantity else '0.000000', 'market_value': str(cents(value)) if value is not None else None, 'unrealized_gain': str(cents(value - holding.cost_basis)) if value is not None else None}


@router.get('/portfolios')
def portfolios(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [public(item) for item in rows(db, m.Portfolio, user.id, page)]


@router.post('/portfolios', status_code=201)
def create_portfolio(data: s.PortfolioCreate, user=Depends(current_user), db=Depends(get_db)):
    portfolio = m.Portfolio(user_id=user.id, name=data.name)
    db.add(portfolio)
    db.flush()
    return public(portfolio)


@router.patch('/portfolios/{portfolio_id}')
def update_portfolio(portfolio_id: UUID, data: s.PortfolioCreate, user=Depends(current_user), db=Depends(get_db)):
    portfolio = owned(db, m.Portfolio, portfolio_id, user.id)
    portfolio.name = data.name
    return public(portfolio)


@router.delete('/portfolios/{portfolio_id}', status_code=204)
def delete_portfolio(portfolio_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    portfolio = owned(db, m.Portfolio, portfolio_id, user.id, lock=True)
    if db.scalar(select(m.Holding.id).where(m.Holding.portfolio_id == portfolio.id).limit(1)):
        fail(409, 'portfolio_not_empty', 'Portfolio with holdings cannot be deleted')
    db.delete(portfolio)


@router.get('/portfolio')
def portfolio_summary(portfolio_id: UUID | None = None, user=Depends(current_user), db=Depends(get_db)):
    statement = select(m.Holding).where(m.Holding.user_id == user.id).order_by(m.Holding.id)
    if portfolio_id:
        owned(db, m.Portfolio, portfolio_id, user.id)
        statement = statement.where(m.Holding.portfolio_id == str(portfolio_id))
    holdings = db.scalars(statement).all()
    totals = defaultdict(lambda: {'cost_basis': Decimal(0), 'market_value': Decimal(0), 'realized_gain': Decimal(0), 'unrealized_gain': Decimal(0), 'valuation_complete': True})
    for holding in holdings:
        current = totals[holding.currency]
        current['cost_basis'] += holding.cost_basis
        current['realized_gain'] += holding.realized_gain
        if holding.quote_price is None and holding.quantity:
            current['valuation_complete'] = False
        elif holding.quote_price is not None:
            current['market_value'] += holding.quote_price * holding.quantity
    output = []
    for currency, value in sorted(totals.items()):
        value['unrealized_gain'] = value['market_value'] - value['cost_basis']
        if not value['valuation_complete']:
            value['market_value'] = value['unrealized_gain'] = None
        output.append({'currency': currency, **{k: str(cents(v)) if isinstance(v, Decimal) else v for k, v in value.items()}})
    views = []
    for holding in holdings:
        view = holding_view(holding)
        total = totals[holding.currency]
        view['allocation_percent'] = str(cents(holding.quantity * holding.quote_price / total['market_value'] * 100)) if total['valuation_complete'] and total['market_value'] and holding.quote_price is not None else None
        view['unrealized_return_percent'] = str(cents((holding.quantity * holding.quote_price - holding.cost_basis) / holding.cost_basis * 100)) if holding.cost_basis and holding.quote_price is not None else None
        views.append(view)
    purchases = defaultdict(Decimal)
    currencies = {holding.id: holding.currency for holding in holdings}
    for trade in db.scalars(select(m.Trade).where(m.Trade.user_id == user.id, m.Trade.side == 'buy', m.Trade.holding_id.in_([h.id for h in holdings]))):
        currency = currencies[trade.holding_id]
        purchases[currency] += trade.quantity * trade.price + trade.fees
    for total in output:
        total['total_purchases_including_fees'] = str(cents(purchases[total['currency']]))
    return {'holdings': views, 'by_currency': output}


@router.post('/portfolio/holdings', status_code=201)
def create_holding(data: s.HoldingCreate, user=Depends(current_user), db=Depends(get_db)):
    if data.portfolio_id:
        portfolio = owned(db, m.Portfolio, data.portfolio_id, user.id, lock=True)
    else:
        db.scalar(select(m.User).where(m.User.id == user.id).with_for_update())
        available = db.scalars(select(m.Portfolio).where(m.Portfolio.user_id == user.id).limit(2)).all()
        if len(available) > 1:
            fail(422, 'portfolio_required', 'Choose a portfolio when multiple exist')
        portfolio = available[0] if available else None
        if portfolio is None:
            portfolio = m.Portfolio(user_id=user.id, name='My portfolio')
            db.add(portfolio)
            db.flush()
    holding = m.Holding(user_id=user.id, portfolio_id=portfolio.id, **data.model_dump(exclude={'portfolio_id'}))
    db.add(holding)
    db.flush()
    return holding_view(holding)


@router.post('/portfolio/trades', status_code=201)
def create_trade(data: s.TradeCreate, user=Depends(current_user), db=Depends(get_db)):
    holding = owned(db, m.Holding, data.holding_id, user.id, lock=True)
    latest = db.scalar(select(func.max(m.Trade.traded_on)).where(m.Trade.holding_id == holding.id))
    if latest and data.traded_on < latest:
        fail(422, 'trade_order', 'Trade date cannot predate latest recorded trade')
    try:
        quantity, basis, gain = apply_trade(holding.quantity, holding.cost_basis, data.side, data.quantity, data.price, data.fees)
    except ValueError as exc:
        fail(409, 'invalid_trade', str(exc))
    if quantity > Decimal('1000000000') or basis > Decimal('999999999999999999') or abs(holding.realized_gain + gain) > Decimal('999999999999999999'):
        fail(409, 'holding_limit', 'Holding arithmetic limit exceeded')
    holding.quantity, holding.cost_basis = quantity, basis
    holding.realized_gain = six(holding.realized_gain + gain)
    trade = m.Trade(user_id=user.id, holding_id=holding.id, realized_gain=gain, **data.model_dump(exclude={'holding_id'}))
    db.add(trade)
    db.flush()
    return public(trade)


@router.get('/portfolio/trades')
def trades(holding_id: UUID | None = None, page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    conditions = []
    if holding_id:
        owned(db, m.Holding, holding_id, user.id)
        conditions.append(m.Trade.holding_id == str(holding_id))
    return [public(item) for item in rows(db, m.Trade, user.id, page, *conditions)]


@router.put('/portfolio/holdings/{holding_id}/quote')
def quote(holding_id: UUID, data: s.QuoteUpdate, user=Depends(current_user), db=Depends(get_db)):
    holding = owned(db, m.Holding, holding_id, user.id, lock=True)
    holding.quote_price, holding.quote_date, holding.quote_source = data.price, data.as_of, data.source
    return holding_view(holding)


@router.put('/portfolio/holdings/{holding_id}/screening')
def screening(holding_id: UUID, data: s.ScreeningUpdate, user=Depends(current_user), db=Depends(get_db)):
    holding = owned(db, m.Holding, holding_id, user.id, lock=True)
    assessment = screen(data.model_dump(mode='json'))
    holding.screening_status = assessment['status']
    holding.screening_source, holding.screening_date, holding.screening_notes = data.source, data.assessed_on, data.notes
    holding.screening_assessment = assessment
    db.add(m.ScreeningRecord(user_id=user.id, holding_id=holding.id, assessment=assessment))
    db.flush()
    return holding_view(holding)


@router.get('/portfolio/holdings/{holding_id}/screenings')
def screening_history(holding_id: UUID, page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    owned(db, m.Holding, holding_id, user.id)
    return [public(record) for record in rows(db, m.ScreeningRecord, user.id, page, m.ScreeningRecord.holding_id == str(holding_id))]


@router.get('/education/investing')
def education(user=Depends(current_user)):
    return [{'id': 'business-activities', 'title': 'Review business activities', 'description': 'Check revenue sources and excluded activities with qualified guidance.'}, {'id': 'ratios', 'title': 'Understand screening ratios', 'description': 'Methodologies differ. Missing or stale statements make screening uncertain.'}, {'id': 'ongoing-review', 'title': 'Review regularly', 'description': 'Manual screening is not certification or investment advice; values and business activities change.'}]
