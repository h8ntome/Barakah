from datetime import date
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator, model_validator

Money = Annotated[Decimal, Field(ge=0, le=Decimal('999999999.99'), max_digits=11, decimal_places=2, allow_inf_nan=False)]
PositiveMoney = Annotated[Decimal, Field(gt=0, le=Decimal('999999999.99'), max_digits=11, decimal_places=2, allow_inf_nan=False)]
Quantity = Annotated[Decimal, Field(gt=0, le=Decimal('1000000000'), max_digits=16, decimal_places=6, allow_inf_nan=False)]
Currency = Literal['USD', 'EUR', 'GBP', 'PKR', 'SAR', 'AED']
Name = Annotated[str, Field(min_length=1, max_length=80)]
Password = Annotated[str, Field(min_length=12, max_length=128)]


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class Login(Input):
    # Password whitespace is significant, unlike human-readable names.
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)
    email: EmailStr
    password: Annotated[str, Field(min_length=1, max_length=128)]


class Register(Login):
    password: Password
    display_name: Name

    @field_validator('display_name')
    @classmethod
    def clean_name(cls, value):
        if not value.strip():
            raise ValueError('Display name is required')
        return value.strip()


class ProfileUpdate(Input):
    display_name: Name | None = None
    ai_consent: bool | None = None
    country: Annotated[str, Field(pattern=r'^[A-Z]{2}$')] | None = None
    timezone: Annotated[str, Field(max_length=64)] | None = None
    language: Annotated[str, Field(pattern=r'^[a-z]{2,3}(-[A-Z]{2})?$')] | None = None
    currency: Currency | None = None

    @field_validator('timezone')
    @classmethod
    def valid_timezone(cls, value):
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
        if value is not None:
            try:
                ZoneInfo(value)
            except (ZoneInfoNotFoundError, ValueError):
                raise ValueError('Unknown IANA timezone')
        return value


class PasswordChange(Input):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)
    current_password: Annotated[str, Field(min_length=1, max_length=128)]
    new_password: Password


class ResetRequest(Input):
    email: EmailStr


class ResetConfirm(Input):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)
    token: Annotated[str, Field(min_length=20, max_length=200)]
    new_password: Password


class DeleteUser(Input):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=False)
    password: Annotated[str, Field(min_length=1, max_length=128)]


class AccountCreate(Input):
    name: Name
    currency: Currency
    account_type: Literal['cash', 'bank', 'savings', 'investment'] = 'cash'
    opening_balance: Money = Decimal('0.00')


class AccountUpdate(Input):
    name: Name | None = None
    account_type: Literal['cash', 'bank', 'savings', 'investment'] | None = None


class TransactionCreate(Input):
    account_id: UUID
    kind: Literal['income', 'expense']
    amount: PositiveMoney
    category: Name
    description: Annotated[str, Field(max_length=500)] = ''
    occurred_on: date


class TransferCreate(Input):
    from_account_id: UUID
    to_account_id: UUID
    amount: PositiveMoney
    occurred_on: date


class BudgetCreate(Input):
    category: Name
    currency: Currency
    amount: PositiveMoney
    month: Annotated[str, Field(pattern=r'^\d{4}-(0[1-9]|1[0-2])$')]

    @field_validator('month')
    @classmethod
    def valid_month(cls, value):
        date.fromisoformat(value + '-01')
        return value


class Assets(Input):
    cash: Money
    investments: Money
    gold: Money
    silver: Money = Decimal('0.00')
    business: Money
    liabilities: Money


class ZakatProfileInput(Input):
    currency: Currency
    assets: Assets
    nisab_method: Literal['manual', 'gold', 'silver']
    manual_nisab: PositiveMoney | None = None
    gold_price_per_gram: Quantity | None = None
    silver_price_per_gram: Quantity | None = None
    price_source: Annotated[str, Field(min_length=1, max_length=200)]
    valuation_date: date
    haul_start: date | None = None
    haul_complete: bool = False
    rate: Annotated[Decimal, Field(gt=0, le=1, max_digits=7, decimal_places=6)] = Decimal('0.025')

    @model_validator(mode='after')
    def required_metadata(self):
        field = {'manual': 'manual_nisab', 'gold': 'gold_price_per_gram', 'silver': 'silver_price_per_gram'}[self.nisab_method]
        if getattr(self, field) is None:
            raise ValueError(f'{field} is required for this nisab method')
        if self.haul_start and self.haul_start > self.valuation_date:
            raise ValueError('Haul start cannot follow valuation date')
        return self


class GivingCreate(Input):
    amount: PositiveMoney
    currency: Currency
    paid_on: date
    category: Name = 'general'
    recipient: Annotated[str, Field(min_length=1, max_length=120)]
    note: Annotated[str, Field(max_length=500)] = ''


class ZakatPaymentCreate(GivingCreate):
    history_id: UUID | None = None


class CauseCreate(Input):
    title: Annotated[str, Field(min_length=1, max_length=120)]
    category: Name
    description: Annotated[str, Field(min_length=1, max_length=1000)]
    currency: Currency


class DonationCreate(Input):
    cause_id: UUID
    amount: PositiveMoney
    currency: Currency


class GoalCreate(Input):
    name: Name
    currency: Currency
    target_amount: PositiveMoney
    target_date: date | None = None


class ContributionCreate(Input):
    amount: PositiveMoney


class HoldingCreate(Input):
    portfolio_id: UUID | None = None
    symbol: Annotated[str, Field(pattern=r'^[A-Z0-9.\-]{1,20}$')]
    name: Name
    currency: Currency


class TradeCreate(Input):
    holding_id: UUID
    side: Literal['buy', 'sell']
    quantity: Quantity
    price: Quantity
    fees: Money = Decimal('0.00')
    traded_on: date


class QuoteUpdate(Input):
    price: Quantity
    as_of: date
    source: Annotated[str, Field(min_length=1, max_length=200)]


class AdvisorMessage(Input):
    text: Annotated[str, Field(min_length=1, max_length=1000)]
    conversation_id: UUID | None = None


class AdCreate(Input):
    title: Annotated[str, Field(min_length=1, max_length=120)]
    body: Annotated[str, Field(min_length=1, max_length=500)]
    url: Annotated[str, Field(min_length=9, max_length=1000)]
    context: Literal['dashboard', 'giving', 'education']
    approved: bool = False
    active: bool = False
    starts_on: date | None = None
    ends_on: date | None = None

    @model_validator(mode='after')
    def valid_window(self):
        if self.starts_on and self.ends_on and self.starts_on > self.ends_on:
            raise ValueError('Campaign end precedes start')
        return self

    @field_validator('url')
    @classmethod
    def secure_url(cls, value):
        from urllib.parse import urlparse
        parsed = urlparse(value)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('HTTPS URL required without credentials')
        return value


class AdUpdate(Input):
    title: Annotated[str, Field(min_length=1, max_length=120)] | None = None
    body: Annotated[str, Field(min_length=1, max_length=500)] | None = None
    url: Annotated[str, Field(min_length=9, max_length=1000)] | None = None
    context: Literal['dashboard', 'giving', 'education'] | None = None
    approved: bool | None = None
    active: bool | None = None
    starts_on: date | None = None
    ends_on: date | None = None

    @field_validator('url')
    @classmethod
    def secure_url(cls, value):
        return AdCreate.secure_url(value) if value is not None else value


class AdEventCreate(Input):
    kind: Literal['impression', 'click']


class PortfolioCreate(Input):
    name: Name


class ScreeningUpdate(Input):
    prohibited_business: bool | None = None
    debt_to_assets: Annotated[Decimal, Field(ge=0, le=100, decimal_places=6)] | None = None
    interest_income_to_revenue: Annotated[Decimal, Field(ge=0, le=100, decimal_places=6)] | None = None
    interest_assets_to_assets: Annotated[Decimal, Field(ge=0, le=100, decimal_places=6)] | None = None
    debt_threshold: Annotated[Decimal, Field(ge=0, le=1, decimal_places=6)] = Decimal('0.30')
    income_threshold: Annotated[Decimal, Field(ge=0, le=1, decimal_places=6)] = Decimal('0.05')
    interest_assets_threshold: Annotated[Decimal, Field(ge=0, le=1, decimal_places=6)] = Decimal('0.30')
    source: Annotated[str, Field(min_length=1, max_length=200)]
    methodology_source: Annotated[str, Field(min_length=1, max_length=200)] = 'Illustrative configurable educational checks, not a scholarly standard'
    assessed_on: date
    notes: Annotated[str, Field(max_length=1000)] = ''
