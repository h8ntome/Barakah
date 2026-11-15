"""Boundary for a future licensed market feed; missing data is never a quote."""
from typing import Protocol
from fastapi import APIRouter, Depends, Query
from .security import current_user
from .common import fail


class MarketDataProvider(Protocol):
    def quote(self, symbol: str, currency: str) -> dict | None: ...
    def metal_prices(self, currency: str) -> dict | None: ...


class UnconfiguredMarketProvider:
    def quote(self, symbol: str, currency: str) -> None:
        return None

    def metal_prices(self, currency: str) -> None:
        return None


def get_market_provider() -> MarketDataProvider:
    # No licensed feed configured. Manual valuations are owned holding/profile data,
    # not reusable global market quotes or evidence of a company's fundamentals.
    return UnconfiguredMarketProvider()


router = APIRouter(tags=['market data'])


@router.get('/stocks/{symbol}')
def stock(symbol: str, currency: str = Query('USD', pattern='^[A-Z]{3}$'), user=Depends(current_user)):
    quote = get_market_provider().quote(symbol, currency)
    if quote is None:
        fail(503, 'market_provider_unavailable', 'No market feed configured. Enter a dated manual holding valuation; it will not be labeled live.')
    return quote


@router.get('/zakat/metal-prices')
def metals(currency: str = Query('USD', pattern='^[A-Z]{3}$'), user=Depends(current_user)):
    prices = get_market_provider().metal_prices(currency)
    if prices is None:
        return {'currency': currency, 'prices': None, 'source': 'manual_entry_required', 'is_live': False}
    return prices
