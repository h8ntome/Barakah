# Executed test results — 2026-11-15

## Environment and evidence scope

macOS27.0.1 (Apple Silicon), Python3.13.5, Node26.12.1/npm11.20.0, agent-browser0.41.1 with real Chromium, PostgreSQL17.11. Frontend production build served with actual FastAPI at `http://127.0.0.1:8081`; SQLite `/tmp/barakah-audit/app.db`, private reset outbox `/tmp/barakah-audit/outbox`. PostgreSQL tests create/drop random isolated schemas in dedicated `barakah_audit_20261115`, never application tables. Backend fixtures apply actual Alembic migrations, not `create_all`.

Final integrated code passed these commands. Logs/screenshots are in `audit/artifacts/`. Earlier worker-only results are not substituted for the parent integration runs.

| Executed check | Result |
|---|---|
| Backend SQLite: `(cd backend && .venv/bin/python -m pytest -q)` | **113 passed**,0 failed, one upstream Starlette/httpx deprecation warning |
| Backend PostgreSQL: `(cd backend && TEST_DATABASE_URL='postgresql+psycopg:///barakah_audit_20261115' .venv/bin/python -m pytest -q)` | **113 passed**,0 failed, same warning |
| Fresh supported Python3.13 environment installed from `backend/requirements.txt` using `uv venv`/`uv pip install`, then full backend suite | **113 passed**,0 failed; clean-install and test logs retained |
| Frontend: `npm test --prefix barakah-ui` | **64 passed**,0 failed,0 skipped |
| Production frontend: `npm run build --prefix barakah-ui` | Passed;1600 modules; JS229.23kB/69.92kB gzip at final run |
| SQLite schema parity: `DATABASE_URL=sqlite:////tmp/barakah-audit/app.db .venv/bin/alembic check` from backend | No new upgrade operations detected |
| `auth_demo.py` real browser | **20 checks passed**: mandatory registration/database hash, logout/login/refresh, invalid credentials, duplicate rejection, two-demo isolation, edits/reload/reset |
| `journey.py` real browser | **31 checks passed**: full registration→accounts→income/expense→budget→zakat/payment→sadaqah→goal→portfolio→settings→AI unavailable→reload/logout/login |
| `finance_corrections.py` real browser | **23 checks passed**: exact requested money cases; transaction/budget/goal/contribution/sadaqah/payment edit/delete and persistence |
| `isolation.py` real Chromium API requests | **21 checks passed**: UserB cannot PATCH/DELETE A's accounts/transactions/budgets/sadaqah/goals/holdings, reference A's account, read A's lists or perform admin actions; A remains unchanged |
| `restart_persistence.py` | **6 checks passed**: disposable on-disk database, actual backend process stop/restart, committed exact balance/FKs, refresh/login and records survive |
| `responsive.py` | **22 checks passed**: five destinations at1280/768/390/320px, no document overflow, persistent navigation reachable, keyboard Tab and no uncaught exceptions |
| `reset_flow.py` | **4 checks passed**: real browser private-outbox reset, URL-token removal, new-password login; no external email claimed |
| `portfolio_repairs.py` | **One complete browser journey passed**:10×50→12×50, invalid oversell rollback/draft retained, latest-trade removal, metadata edit,100% allocation, zero quote, screening, portfolio selection and confirmed cascade deletion;320/1280px |
| Authenticated dashboard smoke:50 real HTTP requests, concurrency4 | **50 passed**,0 failed; median2.166ms, p95 66.828ms, max184.893ms; local bounded probe only |
| `npm audit --json` |0 known vulnerabilities |
| `pip-audit` against complete installed Python package/version inventory |0 known vulnerabilities |
| Impeccable detector over `barakah-ui/src` | `[]` findings; not a full accessibility certification |
| `git diff --check` | Passed |
| Known public homepage and `/api/v1/health` | **Both HTTP404 — external release blocker** |

The seven counted browser scripts total **127 successful named checks**, plus the separate portfolio journey. These are not127 independently isolated test cases; see each script for assertions. No frontend mocks are used as proof of backend correctness. `journey.py` briefly aborts one real transaction request to test failure/draft recovery, removes the interception, then performs the real successful backend mutation.

## Reproduce browser runs

Install the agent-browser CLI/Chromium separately if unavailable. Run the app against an isolated test database; synthetic accounts remain there unless a test explicitly deletes its own account.

```sh
DATABASE_URL=sqlite:////tmp/barakah-audit/app.db \
RESET_OUTBOX=/tmp/barakah-audit/outbox PORT=8081 bash scripts/start-local.sh
```

In another terminal:

```sh
export BARAKAH_UI_URL=http://127.0.0.1:8081
BARAKAH_TEST_DB=/tmp/barakah-audit/app.db python3 tests/e2e/auth_demo.py
python3 tests/e2e/journey.py
python3 tests/e2e/finance_corrections.py
python3 tests/e2e/isolation.py
python3 tests/e2e/portfolio_repairs.py
python3 tests/e2e/responsive.py
BARAKAH_API_URL=http://127.0.0.1:8081/api/v1 \
BARAKAH_RESET_OUTBOX=/tmp/barakah-audit/outbox python3 tests/e2e/reset_flow.py
python3 tests/e2e/restart_persistence.py
```

Keep the normal authentication rate limit enabled; if running many suites rapidly against one process, allow its one-minute window to elapse instead of disabling protection. Restart test provisions its own temporary backend/database and cleans it up. Other scripts refuse non-loopback test URLs.

## Security and data evidence

Backend coverage includes credential hashing, mass-assignment rejection, cookie/CSRF/origin checks, expiry/rotation/revocation, concurrent refresh, reset one-use/expiry, rate limiting, owner checks, financial constraints, exact decimals, concurrent overdraft protection, transaction rollback, migration preservation, same-day trade order and safe reversals. Demo seed failure is injected to verify no partial user/financial writes remain. AI tests prohibit network creation and verify no prompt/message persistence, even with consent/context flags set.

Browser tests assert no uncaught page exceptions. Expected HTTP401/409/503 validation/unavailable responses are not JavaScript crashes. Final managed backend log contained no `ERROR`/`Traceback`. Screenshots were captured in actual Chromium and visually inspected, including desktop investment/giving, tablet Home, narrow320px Home/deletion and390px Chat/Zakat. Viewport tests are emulation, not physical-device validation.

## Failed attempts and corrective work

Initial failures were not suppressed: demo tests exposed decimal-string scale mismatches between databases; a legacy validation assertion forbade a field name; a goal draft fixture lacked the new notes field; a JSX closing brace caused a build failure and was fixed before commit. Browser helpers initially selected a hidden duplicate disclosure/redeclared a global and expected focus to remain in-page after the last navigation tab. Those test defects were corrected; actual finance/refresh behavior was re-executed. `FIXES.md` documents the distinctions.

A requirements-resolution `pip-audit` attempt used Python3.14 and failed because pinned psycopg-binary3.2.9 does not target that interpreter; a3.13 resolver attempt hit local ensurepip SIGABRT. Instead, the **complete installed supported3.13 environment** was inventoried with `importlib.metadata`, then audited with `uvx pip-audit --disable-pip --no-deps -r /tmp/barakah-audit/installed-python.txt -f json`. Every installed package was included; no vulnerable dependency was skipped. This does not establish fresh-install compatibility on unsupported Python versions.

A separate clean Python3.13 installation with `uv` subsequently succeeded and its full backend suite passed113/113, avoiding the local ensurepip limitation. Standard pip or the documented uv alternative may be used.

No test was removed merely to pass. Fake-AI behavioral tests were replaced to match the explicit unavailable-only requirement while retaining security/history coverage; see `AI_INTEGRATION.md`.

## Not verified

Public deployment and the user's exact original failure URL, external SMTP delivery, Docker runtime, physical mobile devices, non-Chromium engines, full screen-reader/penetration testing and production load/capacity. No AI model was downloaded, invoked or tested. `benchmark/` is unchanged.
