"""Seed or delete a private, fictional demo account on a loopback Barakah API.

python3 scripts/demo.py --email judge@example.com
python3 scripts/demo.py --email judge@example.com --delete-test-account
Password is prompted, never fixed or printed. Refuses non-loopback endpoints.
"""
import argparse
from datetime import date
import getpass
import json
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    parser.add_argument('--email', required=True)
    parser.add_argument('--date', default=date.today().isoformat())
    parser.add_argument('--delete-test-account', action='store_true')
    args = parser.parse_args()
    parsed = urllib.parse.urlparse(args.url)
    if parsed.hostname not in {'127.0.0.1', 'localhost', '::1'} or parsed.scheme != 'http':
        parser.error('Demo setup is restricted to a loopback HTTP API.')
    day = date.fromisoformat(args.date).isoformat()
    password = getpass.getpass('Private demo account password (12+ characters): ')
    token = None

    def api(method, path, body=None):
        headers = {'Content-Type': 'application/json', 'Origin': 'http://localhost:5173'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(args.url.rstrip('/') + '/api/v1' + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            # Do not print tokens or supplied financial request bodies.
            raise SystemExit(f'{method} {path} failed with HTTP {error.code}; inspect API logs or OpenAPI.') from None

    if args.delete_test_account:
        token = api('POST', '/auth/login', {'email': args.email, 'password': password})['access_token']
        api('DELETE', '/auth/me', {'password': password})
        print('Account and its associated personal data deleted.')
        return

    token = api('POST', '/auth/register', {'email': args.email, 'password': password, 'display_name': 'Fictional Demo'})['access_token']
    account = api('POST', '/accounts', {'name': 'Fictional checking', 'currency': 'USD', 'opening_balance': '1000.00'})
    for kind, amount, category, description in [
        ('income', '4000.00', 'Salary', 'Fictional monthly salary'),
        ('expense', '600.00', 'Food', 'Fictional grocery total'),
        ('expense', '1200.00', 'Housing', 'Fictional rent'),
    ]:
        api('POST', '/transactions', {'account_id': account['id'], 'kind': kind, 'amount': amount, 'category': category, 'description': description, 'occurred_on': day})
    api('POST', '/budgets', {'category': 'Food', 'currency': 'USD', 'amount': '800.00', 'month': day[:7]})
    api('PUT', '/zakat/profile', {
        'currency': 'USD', 'assets': {'cash': '12000.00', 'investments': '0.00', 'gold': '0.00', 'business': '0.00', 'liabilities': '1000.00'},
        'nisab_method': 'gold', 'gold_price_per_gram': '80.00', 'price_source': 'Fictional manual example, NOT live',
        'valuation_date': day, 'haul_complete': True, 'rate': '0.025',
    })
    history = api('POST', '/zakat/history', {})
    api('POST', '/zakat/payments', {'history_id': history['id'], 'amount': '100.00', 'currency': 'USD', 'paid_on': day, 'recipient': 'Fictional recipient', 'note': 'Tracking only; no payment sent'})
    api('POST', '/sadaqah', {'amount': '50.00', 'currency': 'USD', 'paid_on': day, 'recipient': 'Fictional community fund', 'note': 'Fictional record; no money moved'})
    holding = api('POST', '/portfolio/holdings', {'symbol': 'DEMO', 'name': 'Fictional Example Holding', 'currency': 'USD'})
    api('POST', '/portfolio/trades', {'holding_id': holding['id'], 'side': 'buy', 'quantity': '10', 'price': '20.00', 'fees': '1.00', 'traded_on': day})
    api('PUT', f"/portfolio/holdings/{holding['id']}/quote", {'price': '21.00', 'as_of': day, 'source': 'Fictional manual quote, NOT live'})
    api('PATCH', '/auth/profile', {'ai_consent': True})
    api('POST', '/advisor/messages', {'text': 'Explain a simple monthly budget using fictional examples.'})
    print('Fictional demo created. Log in using the email and private password you supplied.')
    print('No payment, bank connection, live quote or certified screening was performed.')


if __name__ == '__main__':
    main()
