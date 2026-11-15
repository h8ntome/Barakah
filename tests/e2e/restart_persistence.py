"""Start, stop and restart the actual backend with a disposable on-disk database."""
import json
import os
from pathlib import Path
import secrets
import socket
import sqlite3
import subprocess
import tempfile
import time
import urllib.request
import journey as j

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / 'backend' / '.venv' / 'bin' / 'python'


def main():
    with tempfile.TemporaryDirectory(prefix='barakah-restart-') as directory:
        database = Path(directory) / 'test.db'
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]
        j.URL = f'http://127.0.0.1:{port}'
        env = {**os.environ, 'DATABASE_URL': 'sqlite:///' + str(database),
               'ENVIRONMENT': 'test', 'SECRET_KEY': secrets.token_hex(32),
               'ALLOWED_ORIGINS': j.URL, 'FRONTEND_DIST': str(ROOT / 'barakah-ui' / 'dist'), 'AI_MODE': 'unavailable'}
        subprocess.run([str(PYTHON), '-m', 'alembic', 'upgrade', 'head'], cwd=ROOT / 'backend', env=env, check=True, capture_output=True)
        with open(Path(directory) / 'server.log', 'w') as log:
            def start():
                process = subprocess.Popen([str(PYTHON), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(port), '--no-access-log'], cwd=ROOT / 'backend', env=env, stdout=log, stderr=log)
                for _ in range(100):
                    if process.poll() is not None: raise AssertionError('Backend startup failed')
                    try:
                        with urllib.request.urlopen(j.URL + '/api/v1/health', timeout=1) as response:
                            if response.status == 200: return process
                    except OSError: pass
                    time.sleep(.1)
                process.terminate(); process.wait(timeout=10)
                raise AssertionError('Backend readiness deadline exceeded')
            process = start()
            try:
                email, password = 'restart-' + secrets.token_hex(8) + '@example.com', secrets.token_urlsafe(24)
                j.browser('open', j.URL); j.click('New account'); j.fill('Display name', 'Restart QA'); j.fill('Email address', email); j.fill('New password', password); j.click('Create account'); j.wait('Welcome to Barakah.')
                j.click('Accounts'); j.fill('Account name', 'Persistent cash'); j.fill('Opening balance', '1000.00'); j.click('Add account'); j.wait('Persistent cash')
                j.click('Transactions'); j.select('Transaction account', 'Persistent cash (USD)'); j.select('Transaction type', 'income'); j.fill('Transaction amount', '500.00'); j.fill('Category', 'Salary'); j.fill('Description', 'Restart survivor'); j.click('Record transaction'); j.wait('Restart survivor')
                process.terminate(); process.wait(timeout=10)
                with sqlite3.connect(database) as db:
                    assert db.execute('select count(*) from transactions').fetchone()[0] == 1
                    assert db.execute('select balance from accounts').fetchone()[0] == '1500.00'
                    assert db.execute('pragma foreign_key_check').fetchall() == []
                j.checks.append('committed exact balances and foreign keys survive process stop')
                process = start()
                j.browser('reload'); j.check('session refresh after backend restart', 'Welcome to Barakah.')
                j.check('balance survives backend restart', '$1,500.00')
                j.click('Transactions'); j.check('transaction survives backend restart', 'Restart survivor')
                j.click('Settings'); j.click('Sign out'); j.fill('Email address', email); j.fill('Password', password); j.click('Sign in'); j.check('login after restart retains data', '$1,500.00')
                assert not j.browser('errors').strip()
                j.checks.append('no uncaught browser exceptions')
                print(json.dumps({'passed': len(j.checks), 'failed': 0, 'checks': j.checks}, indent=2))
            finally:
                process.terminate(); process.wait(timeout=10)


if __name__ == '__main__':
    try:
        main()
    finally:
        j.browser('close')
