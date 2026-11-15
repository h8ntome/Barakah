"""Fictional, owner-isolated demo data, using the same validated finance operations."""
import secrets
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from . import finance, giving, portfolio, schemas as s
from .common import fail
from .db import get_db
from .models import User
from .security import auth_limit, current_user, hasher, issue_session

router = APIRouter(prefix='/auth/demo', tags=['demo'])


def seed(db, response):
    now = datetime.now(timezone.utc)
    # Bounded opportunistic cleanup; never targets regular accounts.
    expired = db.scalars(select(User).where(User.is_demo.is_(True), User.demo_expires_at <= now).limit(100)).all()
    for old in expired:
        db.delete(old)
    user = User(email=f'demo-{secrets.token_hex(16)}@example.invalid', display_name='Fictional Demo',
                password_hash=hasher.hash(secrets.token_urlsafe(48)), is_demo=True,
                demo_expires_at=now + timedelta(hours=24))
    db.add(user)
    db.flush()
    day = date.today()
    cash = finance.create_account(s.AccountCreate(name='Demo checking', currency='USD', opening_balance='1350.00'), user, db)
    finance.create_account(s.AccountCreate(name='Demo savings', account_type='savings', currency='USD', opening_balance='12000.00'), user, db)
    for kind, amount, category in [('income', '4500.00', 'Salary'), ('expense', '1500.00', 'Housing'), ('expense', '400.00', 'Food'), ('expense', '300.00', 'Transport'), ('expense', '250.00', 'Utilities'), ('expense', '400.00', 'Household')]:
        finance.create_transaction(s.TransactionCreate(account_id=cash['id'], kind=kind, amount=amount, category=category,
                                   description=f'Fictional {category.lower()}', occurred_on=day), user, db)
    # Prior-month history produces meaningful stored-data charts without changing cash.
    previous = day.replace(day=1) - timedelta(days=1)
    for kind, amount, category in [('income', '4200.00', 'Salary'), ('expense', '4200.00', 'Household')]:
        finance.create_transaction(s.TransactionCreate(account_id=cash['id'], kind=kind, amount=amount, category=category,
                                   description='Fictional previous month', occurred_on=previous), user, db)
    for category, amount in [('Food', '500.00'), ('Housing', '1500.00'), ('Transport', '350.00')]:
        finance.create_budget(s.BudgetCreate(category=category, currency='USD', amount=amount, month=day.strftime('%Y-%m')), user, db)
    giving.put_profile(s.ZakatProfileInput(currency='USD', assets=s.Assets(cash='3000.00', savings='12000.00', investments='0', gold='0', business='0', liabilities='0'),
                       nisab_method='manual', manual_nisab='5000.00', price_source='Fictional threshold, not current market data', valuation_date=day,
                       haul_complete=True), user, db)
    giving.create_history(user, db)
    for amount, recipient in [('50.00', 'Fictional community kitchen'), ('75.00', 'Fictional education fund')]:
        giving.create_sadaqah(s.GivingCreate(amount=amount, currency='USD', paid_on=day, recipient=recipient, note='Fictional record; no payment sent'), user, db)
    goal = giving.create_goal(s.GoalCreate(name='Hajj savings', currency='USD', target_amount='5000.00', target_date=day + timedelta(days=365)), user, db)
    giving.contribute(goal['id'], s.ContributionCreate(amount='1250.00'), user, db)
    for symbol, name, quantity, price in [('DEMO-A', 'Fictional screened equity example', '100', '50'), ('DEMO-B', 'Fictional sukuk example', '50', '50'), ('DEMO-C', 'Fictional gold example', '10', '100')]:
        holding = portfolio.create_holding(s.HoldingCreate(symbol=symbol, name=name, currency='USD'), user, db)
        portfolio.create_trade(s.TradeCreate(holding_id=holding['id'], side='buy', quantity=quantity, price=price, traded_on=day), user, db)
        portfolio.quote(holding['id'], s.QuoteUpdate(price=price, as_of=day, source='Fictional manual valuation; NOT live'), user, db)
    return issue_session(db, user, response)


@router.post('', status_code=201, dependencies=[Depends(auth_limit)])
def start_demo(response: Response, db=Depends(get_db)):
    return seed(db, response)


@router.post('/reset', dependencies=[Depends(auth_limit)])
def reset_demo(response: Response, user=Depends(current_user), db=Depends(get_db)):
    if not user.is_demo:
        fail(403, 'not_demo', 'Only a demonstration workspace can be reset')
    db.delete(user)
    db.flush()
    return seed(db, response)
