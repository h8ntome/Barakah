# Executed test results

Final verification: **2026-11-15**, macOS arm64, Python 3.13.5, native PostgreSQL 17.11, React 18/Vite 7. PostgreSQL used a dedicated integration database; pytest created and removed isolated random schemas. No Docker daemon was available.

| Check | Actual result |
|---|---|
| Backend SQLite `python -m pytest -q` | **70 passed, 1 skipped**; skip is the PostgreSQL-only concurrency regression |
| Backend PostgreSQL `TEST_DATABASE_URL=… python -m pytest -q` | **71 passed** |
| Frontend `npm test` | **53 passed**, zero failures |
| Frontend `npm run build` | Passed; Vite production output generated |
| `alembic upgrade head` and `alembic check` on integration PostgreSQL | Passed; no new upgrade operations |
| Migration regressions within both suites | Empty DB, downgrade/upgrade parity, legacy screening preservation, old-revision readiness rejection |
| Real Chromium `tests/e2e/journey.py` | **29 assertions passed**, 27.8s final run |
| Real Chromium `tests/e2e/reset_flow.py` | **4 assertions passed**, private development outbox |
| Sponsored placement browser check | Visible impression and actual link click each persisted once |
| Bounded readiness probe | **50/50 HTTP 200**, concurrency 4, median 2.129ms, p95 6.426ms, max 6.770ms |
| Impeccable mechanical detector on final changed screens | No findings (`[]`) |
| `npm audit` | Zero known vulnerabilities reported |
| `pip-audit` against the final installed/frozen backend environment | Zero known vulnerabilities reported |
| Fictional demo seed/read/delete | Completed against isolated local API |

The SQLite/PostgreSQL suites run substantially the same tests: do not treat their sum as unique coverage. Frontend checks include retained legacy-mock tests as well as live-adapter utilities; real integration evidence is separate. The load probe hits **readiness only**, on this local machine, and is not an authenticated-workload or production-capacity benchmark.

One upstream Starlette TestClient warning remains: httpx compatibility is deprecated in favor of a future httpx2 transition. No tests failed. HTTP provider fixture tests still exercise actual httpx requests.

## Commands

From repository root, with dependencies installed:

```sh
(cd backend && .venv/bin/python -m pytest -q)
(cd backend && TEST_DATABASE_URL='postgresql+psycopg:///barakah_test' .venv/bin/python -m pytest -q)
(cd backend && DATABASE_URL='postgresql+psycopg:///barakah_test' .venv/bin/alembic upgrade head && DATABASE_URL='postgresql+psycopg:///barakah_test' .venv/bin/alembic check)
(cd barakah-ui && npm test && npm run build && npm audit)
python3 tests/e2e/journey.py
BARAKAH_RESET_OUTBOX=backend/outbox python3 tests/e2e/reset_flow.py
python3 tests/load_smoke.py
# Audit the installed backend rather than resolving for an unrelated Python version:
uv pip freeze --python backend/.venv/bin/python > /tmp/barakah-requirements.txt
uvx pip-audit --no-deps --disable-pip -r /tmp/barakah-requirements.txt
```

Use an isolated local database and the API's actual outbox path. Browser scripts require `agent-browser` plus Chromium and running frontend/API. No credentials or tokens are committed. Final raw outputs are under [evidence/](evidence/).

## Review and defect history

Independent backend/frontend reviews were completed. Fixed findings include stale account-switch responses/retries, expired-token deletion refresh, independent silver/savings/other fields, paginated payment choices, ad events, custom screening validity loss, conversation selector pagination, misleading advisor docs, SQL parameter leakage, fractional gain double rounding, slow-drip provider timeout, stale-schema readiness, and lost pre-migration screening snapshots. Regression tests accompany fixes. The final custom-validity browser check specifically preserves 30 days across save/reload.

The initial dependency audit identified advisories in old PyJWT/Starlette and pytest packages; affected pins were upgraded (FastAPI 0.163.0, Starlette 1.10.0, PyJWT 2.15.1, pytest 9.2.0), then both suites and browser flows passed. Earlier pip-audit attempts failed due to an unrelated Python 3.14 wheel mismatch and a temporary virtualenv bootstrap issue; the successful final audit used the actual installed Python 3.13 environment's frozen dependencies. No audit failures are represented as clean scans.

Earlier browser runs exposed viewport/timing issues in automation, fixed by centered disclosure scrolling and accessible-name waits; they are not counted as final passes. Screenshots were inspected at desktop and 390px width.

Not executed: container startup, actual fine-tuned inference, live markets/metals, external SMTP delivery, production ingress/backup restore, broad browser/accessibility matrix, sustained stress/penetration testing. See [coverage](feature-coverage.md).
