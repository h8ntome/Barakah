# Repairs and engineering decisions

Baseline `6dca92f`; dedicated branch `audit/full-application-fix`. Existing architecture and visual identity retained. No model-training/benchmark changes.

| Severity | Initial issue / cause | Repair | Evidence |
|---|---|---|---|
| P0 launch | Static deployment has no backend; wrong local origin yields403 | `scripts/start-local.sh` builds/serves UI+API on one origin with exact allowlist, migrations and readiness. Origin/CSRF controls remain enabled | Browser auth + restart; public hosting still blocked, see remaining issues |
| P2 auth | Duplicate message unclear; validation generic; HTML API fallback dereferenced null | Clear409 duplicate guidance; validation reports only field names; non-JSON/malformed session responses fail clearly without pretending success | auth and HTTP client tests; browser duplicate/wrong-password checks |
| P1 demo | CLI-only seed, no visible judge entry/reset/expiry | Unique non-admin demo owner, random unexposed password, real persisted template,24h expiry, transactional reset, bounded expired-owner cleanup |20 browser checks, DB isolation/expiry and injected rollback tests |
| P2 session reset | Independent review found demo reset bypassed401 refresh | Authenticated session replacement uses shared request/refresh path before accepting new session | Expired-access client regression; demo reset browser |
| P1 holding/trade corrections | No edit/remove operations; wrong buys permanently affected cost/gains | Owner-checked metadata/removal and explicit destructive confirmation. New ordered trades store exact pre-trade snapshots; latest-only correction/removal restores precise totals atomically |10×50→12×50, oversell rollback, same-day ordering, race tests, browser removal |
| P1 zakat payments | Wrong/duplicate payment could never be corrected | Owned/type-checked PATCH/DELETE, linked snapshot ownership/currency checks; immutable calculations retained | Outstanding$375→$225→$375; cross-user/currency rejection |
| P2 savings | Giving-only wording; no remaining/percent; contributions only increased | Home/Give savings goals, server progress/remaining, contribution edit/delete under goal lock | Hajj25%/$3,750; correction/deletion; browser refresh |
| P2 dashboard | Missing overview history/goals/budgets/zakat/portfolio visualization | Owned stored-data summaries, category bars, budget/goal indicators and portfolio allocation bars; tracked-net-assets label | Dashboard mutation tests and rendered screenshots |
| P2 decimals | PostgreSQL/NUMERIC padding such as5000.000000 failed two-decimal form patterns | Shared input helper removes only insignificant padding beyond allowed precision; never rounds or uses floating-point accounting | Regression tests and name-only goal edit browser |
| P2 screening/quotes | Zero valuation rejected; future evidence looked current; trade filter ignored portfolio | Nonnegative quote type; reject future assessment dates and classify invalid legacy evidence uncertain; owner-checked portfolio filter | Backend parity/portfolio browser tests |
| P2 zakat assumptions | Eligibility distinctions not explicit enough or preserved as explanatory notes | Explain eligible versus excluded assets, jewelry/investment/debt differences and lunar-year attestation; persist classification notes in snapshots | Browser save/reload/history; existing gold/silver/haul/rounding tests retained |
| P1 AI requirement | Deterministic fake advice and local inference path contradicted requested placeholder | Removed both paths; unavailable-only typed boundary,503 without message writes, usable disclosed UI; legacy history readable/deletable | No-network/no-write tests and browser send |
| P2 settings | Clearing country silently sent ignored null | Require valid two-letter country in the existing form instead of silently dropping a blank selection | Build/form validation; normal settings persistence browser |

## Registration diagnosis: known versus unknown

At the pre-existing configured local origin, a real browser registered successfully (201), and read-only SQL confirmed exactly one synthetic user with an Argon2id hash. Logout/login/refresh worked before code changes. A browser on port5182 reproduced403 `origin_forbidden`; that port was not in the explicit allowlist. The known public alias returned404, and `vercel.json` only deployed static frontend assets.

The user's exact failing URL and server response were not supplied. Therefore this audit **does not claim to have proven the exact cause of that particular attempt** or repaired an inaccessible public deployment. It provides a verified same-origin application path and actionable configuration/error feedback without weakening security.

## Test corrections, not deleted failures

- The existing credential-leak assertion forbade the literal field name `password`, rather than the submitted secret value. It now forbids the submitted value, allowing useful field-name feedback while retaining the security intent.
- Demo numeric assertions initially compared database-dependent decimal scale. They now compare Decimal values; SQLite and PostgreSQL both pass. An initial invalid-password fixture accidentally had12 characters; corrected the fixture, not password validation.
- The saved-zakat draft fixture was extended for the new classification-notes field and retains exact amount/weight assertions.
- Old AI-response assertions were replaced because fake advice is expressly prohibited. Historical chat fixtures retain ownership, ordering, deletion and revocation coverage; `AI_INTEGRATION.md` maps all superseded contracts.
- Browser disclosure selection now scopes to visible elements because savings goals appear on both Home and Give. The helper uses an isolated JS scope so repeated calls do not redeclare globals. Keyboard testing starts at a known tab instead of treating legitimate focus departure after the last tab as failure.
- Goal-contribution browser tests reopen the disclosure after list reload. The existing component remount closes it; no persistence failure was hidden.

## Preservation and security

All financial writes use existing validated API/SQLAlchemy transactions. New schema migrations are additive; existing users, trade history and balances remain unchanged. The audit only migrated its own test databases. Destructive UI actions are explicit and owner-scoped. No default admin credentials, production mocks, secret commits or disabled authentication were introduced. Registration's clearer duplicate response intentionally reveals email registration status as requested; login/reset remain generic and auth endpoints are rate-limited.

Independent review found no concrete P0/P1 regression in the reviewed diff and identified the expired demo-reset issue above, which was repaired. This is not a penetration-test guarantee.
