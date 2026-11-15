from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID
from typing import Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from . import models as m, schemas as s
from .db import get_db
from .security import current_user
from .common import cents, fail, json_value, owned, pagination, public, rows

router = APIRouter(tags=['finance'])


def account_view(account):
    return public(account)


def adjust(account, delta):
    balance = account.balance + delta
    if balance < 0:
        fail(409, 'insufficient_funds', 'Operation would overdraw the account')
    if balance > Decimal('999999999999.99'):
        fail(409, 'balance_limit', 'Account balance limit exceeded')
    account.balance = balance


@router.get('/accounts')
def accounts(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [account_view(a) for a in rows(db, m.Account, user.id, page)]


@router.post('/accounts', status_code=201)
def create_account(data: s.AccountCreate, user=Depends(current_user), db=Depends(get_db)):
    account = m.Account(user_id=user.id, name=data.name, currency=data.currency, account_type=data.account_type, balance=data.opening_balance)
    db.add(account)
    db.flush()
    return account_view(account)


@router.get('/accounts/{account_id}')
def account_detail(account_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    return account_view(owned(db, m.Account, account_id, user.id))


@router.patch('/accounts/{account_id}')
def update_account(account_id: UUID, data: s.AccountUpdate, user=Depends(current_user), db=Depends(get_db)):
    account = owned(db, m.Account, account_id, user.id, lock=True)
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(account, key, value)
    return account_view(account)


@router.delete('/accounts/{account_id}', status_code=204)
def delete_account(account_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    account = owned(db, m.Account, account_id, user.id, lock=True)
    if db.scalar(select(m.Transaction.id).where(m.Transaction.account_id == account.id).limit(1)):
        fail(409, 'account_has_transactions', 'Account with ledger entries cannot be deleted')
    db.delete(account)


@router.get('/transactions')
def transactions(sort: Literal['date_desc', 'date_asc'] = 'date_desc', account_id: UUID | None = None, category: str | None = Query(None, max_length=80), query: str | None = Query(None, max_length=100), start_date: date | None = None, end_date: date | None = None, page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    conditions = []
    if account_id:
        owned(db, m.Account, account_id, user.id)
        conditions.append(m.Transaction.account_id == str(account_id))
    if category:
        conditions.append(m.Transaction.category == category)
    if query:
        conditions.append(m.Transaction.description.icontains(query, autoescape=True))
    if start_date:
        conditions.append(m.Transaction.occurred_on >= start_date)
    if end_date:
        conditions.append(m.Transaction.occurred_on <= end_date)
    if start_date and end_date and start_date > end_date:
        fail(422, 'validation_error', 'Date range is inverted')
    order = m.Transaction.occurred_on.desc() if sort == 'date_desc' else m.Transaction.occurred_on.asc()
    statement = select(m.Transaction).where(m.Transaction.user_id == user.id, *conditions).order_by(order, m.Transaction.id).limit(page[0]).offset(page[1])
    return [public(t) for t in db.scalars(statement)]


@router.post('/transactions', status_code=201)
def create_transaction(data: s.TransactionCreate, user=Depends(current_user), db=Depends(get_db)):
    account = owned(db, m.Account, data.account_id, user.id, lock=True)
    adjust(account, data.amount if data.kind == 'income' else -data.amount)
    transaction = m.Transaction(user_id=user.id, **data.model_dump(exclude={'account_id'}), account_id=account.id, currency=account.currency)
    db.add(transaction)
    db.flush()
    return public(transaction)


@router.patch('/transactions/{transaction_id}')
def update_transaction(transaction_id: UUID, data: s.TransactionCreate, user=Depends(current_user), db=Depends(get_db)):
    transaction = owned(db, m.Transaction, transaction_id, user.id, lock=True)
    if transaction.transfer_id:
        fail(409, 'transfer_immutable', 'Transfer ledger entries cannot be edited separately')
    # Deterministic account lock order avoids concurrent cross-account edit deadlocks.
    accounts = {key: owned(db, m.Account, key, user.id, lock=True) for key in sorted({transaction.account_id, str(data.account_id)})}
    old, new = accounts[transaction.account_id], accounts[str(data.account_id)]
    reversal = -transaction.amount if transaction.kind == 'income' else transaction.amount
    delta = data.amount if data.kind == 'income' else -data.amount
    if old.id == new.id:
        adjust(old, reversal + delta)
    else:
        adjust(old, reversal)
        adjust(new, delta)
    for key, value in data.model_dump(exclude={'account_id'}).items():
        setattr(transaction, key, value)
    transaction.account_id, transaction.currency = new.id, new.currency
    db.flush()
    return public(transaction)


@router.delete('/transactions/{transaction_id}', status_code=204)
def delete_transaction(transaction_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    transaction = owned(db, m.Transaction, transaction_id, user.id, lock=True)
    if transaction.transfer_id:
        fail(409, 'transfer_immutable', 'Transfer ledger entries cannot be deleted separately')
    account = owned(db, m.Account, transaction.account_id, user.id, lock=True)
    adjust(account, -transaction.amount if transaction.kind == 'income' else transaction.amount)
    db.delete(transaction)


@router.post('/transfers', status_code=201)
def transfer(data: s.TransferCreate, user=Depends(current_user), db=Depends(get_db)):
    if data.from_account_id == data.to_account_id:
        fail(422, 'invalid_transfer', 'Select two different accounts')
    accounts = {key: owned(db, m.Account, key, user.id, lock=True) for key in sorted([str(data.from_account_id), str(data.to_account_id)])}
    source, destination = accounts[str(data.from_account_id)], accounts[str(data.to_account_id)]
    if source.currency != destination.currency:
        fail(422, 'currency_mismatch', 'Transfers require matching currencies; FX is not supported')
    adjust(source, -data.amount)
    adjust(destination, data.amount)
    transfer_id = m.uid()
    for account, kind in [(source, 'transfer_out'), (destination, 'transfer_in')]:
        db.add(m.Transaction(user_id=user.id, account_id=account.id, kind=kind, amount=data.amount, currency=account.currency, category='transfer', occurred_on=data.occurred_on, transfer_id=transfer_id))
    db.flush()
    return json_value({'id': transfer_id, 'from_account_id': source.id, 'to_account_id': destination.id, 'amount': data.amount, 'currency': source.currency})


def budget_view(db, budget):
    entries = db.scalars(select(m.Transaction).where(m.Transaction.user_id == budget.user_id, m.Transaction.currency == budget.currency, m.Transaction.category == budget.category, m.Transaction.kind == 'expense')).all()
    spent = sum((t.amount for t in entries if t.occurred_on.strftime('%Y-%m') == budget.month), Decimal(0))
    return {**public(budget), 'spent': str(cents(spent)), 'remaining': str(cents(budget.amount - spent)), 'exceeded_amount': str(cents(max(Decimal(0), spent - budget.amount))), 'utilization_percent': str(cents(spent / budget.amount * 100))}


@router.get('/budgets')
def budgets(page=Depends(pagination), user=Depends(current_user), db=Depends(get_db)):
    return [budget_view(db, b) for b in rows(db, m.Budget, user.id, page)]


@router.post('/budgets', status_code=201)
def create_budget(data: s.BudgetCreate, user=Depends(current_user), db=Depends(get_db)):
    budget = m.Budget(user_id=user.id, **data.model_dump())
    db.add(budget)
    db.flush()
    return budget_view(db, budget)


@router.patch('/budgets/{budget_id}')
def update_budget(budget_id: UUID, data: s.BudgetCreate, user=Depends(current_user), db=Depends(get_db)):
    budget = owned(db, m.Budget, budget_id, user.id, lock=True)
    for key, value in data.model_dump().items():
        setattr(budget, key, value)
    db.flush()
    return budget_view(db, budget)


@router.delete('/budgets/{budget_id}', status_code=204)
def delete_budget(budget_id: UUID, user=Depends(current_user), db=Depends(get_db)):
    db.delete(owned(db, m.Budget, budget_id, user.id))


@router.get('/dashboard')
def dashboard(month: str | None = Query(None, pattern=r'^\d{4}-(0[1-9]|1[0-2])$'), user=Depends(current_user), db=Depends(get_db)):
    month = month or datetime.now(timezone.utc).strftime('%Y-%m')
    categories = defaultdict(lambda: defaultdict(Decimal))
    totals = defaultdict(lambda: {'balance': Decimal(0), 'income': Decimal(0), 'expenses': Decimal(0), 'total_assets': Decimal(0), 'liabilities': Decimal(0), 'portfolio_value': Decimal(0), 'valuation_complete': True})
    for account in db.scalars(select(m.Account).where(m.Account.user_id == user.id)):
        totals[account.currency]['balance'] += account.balance
        totals[account.currency]['total_assets'] += account.balance
    for transaction in db.scalars(select(m.Transaction).where(m.Transaction.user_id == user.id, m.Transaction.kind.in_(['income', 'expense']))):
        if transaction.occurred_on.strftime('%Y-%m') == month:
            totals[transaction.currency]['income' if transaction.kind == 'income' else 'expenses'] += transaction.amount
            if transaction.kind == 'expense':
                categories[transaction.currency][transaction.category] += transaction.amount
    for holding in db.scalars(select(m.Holding).where(m.Holding.user_id == user.id)):
        if holding.quantity and holding.quote_price is None:
            totals[holding.currency]['valuation_complete'] = False
        elif holding.quote_price is not None:
            totals[holding.currency]['total_assets'] += holding.quantity * holding.quote_price
            totals[holding.currency]['portfolio_value'] += holding.quantity * holding.quote_price
    profile = db.scalar(select(m.ZakatProfile).where(m.ZakatProfile.user_id == user.id))
    if profile:
        totals[profile.data['currency']]['liabilities'] = Decimal(profile.data['assets']['liabilities'])
    output = []
    for currency, values in sorted(totals.items()):
        values['savings'] = values['income'] - values['expenses']
        values['savings_rate_percent'] = cents(values['savings'] / values['income'] * 100) if values['income'] else None
        values['expense_categories'] = {name: str(cents(amount)) for name, amount in categories[currency].items()}
        values['expense_category_percent'] = {name: str(cents(amount / values['expenses'] * 100)) for name, amount in categories[currency].items()} if values['expenses'] else {}
        values['net_worth'] = values['total_assets'] - values['liabilities']
        if not values['valuation_complete']:
            values['total_assets'] = values['net_worth'] = values['portfolio_value'] = None
        output.append({'currency': currency, **{k: str(cents(v)) if isinstance(v, Decimal) else v for k, v in values.items()}})
    from .giving import goal_view, history_view
    from .calculations import zakat_estimate
    latest = db.scalar(select(m.ZakatHistory).where(m.ZakatHistory.user_id == user.id).order_by(m.ZakatHistory.created_at.desc(), m.ZakatHistory.id.desc()).limit(1))
    recent = db.scalars(select(m.Transaction).where(m.Transaction.user_id == user.id).order_by(m.Transaction.occurred_on.desc(), m.Transaction.id.desc()).limit(5))
    return {'display_name': user.display_name, 'month': month, 'by_currency': output,
            'recent_transactions': [public(item) for item in recent],
            'budgets': [budget_view(db, item) for item in db.scalars(select(m.Budget).where(m.Budget.user_id == user.id, m.Budget.month == month))],
            'goals': [goal_view(item) for item in db.scalars(select(m.Goal).where(m.Goal.user_id == user.id).order_by(m.Goal.id).limit(5))],
            'zakat': zakat_estimate(profile.data) if profile else None,
            'latest_zakat_record': history_view(db, latest) if latest else None,
            'asset_basis': 'Account balances plus manually quoted portfolio holdings; liabilities from zakat profile. Other manually classified zakat assets excluded to avoid double counting.'}
