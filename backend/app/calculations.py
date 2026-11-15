"""Pure Decimal financial rules; no HTTP, persistence or claims of religious authority."""
from decimal import Decimal
from .common import cents, six


def zakat_estimate(profile):
    assets = profile['assets']
    total = sum((Decimal(assets.get(key, '0')) for key in ('cash', 'savings', 'investments', 'gold', 'silver', 'business', 'other')), Decimal(0))
    base = max(Decimal(0), total - Decimal(assets['liabilities']))
    method = profile['nisab_method']
    nisab = Decimal(profile['manual_nisab']) if method == 'manual' else Decimal(profile[f'{method}_price_per_gram']) * Decimal(profile.get(f'{method}_nisab_grams', '85' if method == 'gold' else '595'))
    eligible = base >= nisab and profile['haul_complete']
    return {'currency': profile['currency'], 'total_assets': str(cents(total)), 'eligible_base': str(cents(base)), 'nisab': format(nisab, 'f'), 'haul_complete': profile['haul_complete'], 'eligible': eligible, 'estimated_due': str(cents(base * Decimal(profile['rate'])) if eligible else cents(0)), 'methodology': f"manual-wealth-v1: declared deductible debt; {profile.get('gold_nisab_grams', '85')}g gold/{profile.get('silver_nisab_grams', '595')}g silver or manual nisab; user-attested haul; educational estimate, not a ruling", 'valuation_date': profile['valuation_date'], 'price_source': profile['price_source']}


def apply_trade(quantity, cost_basis, side, trade_quantity, price, fees):
    gross = trade_quantity * price
    if side == 'buy':
        return quantity + trade_quantity, six(cost_basis + gross + fees), Decimal(0)
    if trade_quantity > quantity:
        raise ValueError('Cannot sell more than the held quantity')
    if fees > gross:
        raise ValueError('Sell fees cannot exceed proceeds')
    removed_cost = cost_basis if trade_quantity == quantity else six(cost_basis * trade_quantity / quantity)
    return quantity - trade_quantity, six(cost_basis - removed_cost), six(gross - fees - removed_cost)


def screen(data):
    pairs = [('debt_to_assets', 'debt_threshold'), ('interest_income_to_revenue', 'income_threshold'), ('interest_assets_to_assets', 'interest_assets_threshold')]
    missing = [key for key in ['prohibited_business', *(p[0] for p in pairs)] if data.get(key) is None]
    breached = [key for key, threshold in pairs if data.get(key) is not None and Decimal(data[key]) > Decimal(data[threshold])]
    if data.get('prohibited_business') is True:
        breached.append('prohibited_business')
    status = 'non_compliant' if breached else ('uncertain' if missing else 'compliant_under_selected_methodology')
    return {**data, 'status': status, 'methodology_version': 'illustrative-configurable-ratios-v1', 'missing_inputs': missing, 'failed_checks': breached, 'disclaimer': 'User-supplied inputs and thresholds; educational checks only, not certification, a named scholarly standard, or investment advice.'}
