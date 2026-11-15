# Connected frontend validation

**Final parent integration (2026-11-15):** 53 frontend tests pass, production build and npm audit pass, 29 real PostgreSQL-backed browser journey assertions and four reset assertions pass. A real sponsored impression/click was also persisted. Final custom screening validity, conversation selection and opt-in-context documentation fixes are included. See [final evidence](../docs/testing/test-results.md) and [screenshots](../docs/testing/integration-results.md). Sections below retain earlier worker checkpoint history, not the final status.

## Automated evidence

- `npm ci`: passed; 0 audit vulnerabilities reported.
- `npm test`: **31/31 passing** at implementation checkpoint. Includes 15 new API/transport checks and 16 retained legacy fixture/display checks. Legacy mock tests are explicitly named `legacyMockAdapter.test.js`; they do not validate the real backend.
- `npm run build`: passed, Vite 7.3.8. At this checkpoint JS 207.78 kB / 64.60 kB gzip; CSS 30.97 kB / 7.28 kB gzip.
- `git diff --check`: passed.
- Impeccable mechanical detector over changed UI: `[]`.
- No lint script exists; no lint-pass claim.

New automated coverage: exact decimal-string serialization, documented mutation/filter routes, absence of runtime mock selection, concurrent refresh serialization, late-401 token reuse, one-retry bound, session clearing on refresh rejection, logout/rotation ordering, current CSRF header, API error envelope, safe 5xx/network errors, non-retry of financial writes on network errors and query encoding and preserving the session when a confirmation password is wrong.

## Browser evidence performed by frontend worker

Used a unique `agent-browser` session against the replacement worktree Vite on `http://127.0.0.1:5174` (the pre-existing :5173 server was a different checkout and left untouched).

- Rendered and visually inspected sign-in at 390×844, 320×640 and 1440×1000. Original emerald/mint/phone identity and five bottom destinations retained.
- At 320px, document scroll width equals viewport width (320); no horizontal page overflow.
- Submitted test credentials while backend was unavailable: safe error displayed; email/password draft retained; no false success. Browser JavaScript error buffer empty.
- Local screenshots: `/tmp/barakah-frontend-auth.png`, `/tmp/barakah-frontend-auth-320.png`, `/tmp/barakah-frontend-auth-desktop.png` (not committed).

## Integration review gate

The parent orchestrator owns reproducible authenticated real-backend browser E2E and its artifacts. At the checkpoint above, no backend listener was available on :8000; therefore these frontend checks **do not claim** browser-validated registration, authenticated financial mutations, reset delivery or provider inference. Those must be accepted against the actual backend, not the legacy mocks or mocked fetch tests.

Suggested integrated pass:

1. Register/sign out/sign in, reload to restore via cookie, change settings/consent, test password reset and account deletion with isolated test accounts.
2. Create two accounts; record/edit/delete income/expense; transfer; apply description/category/account/date filters; verify server dashboard month and budget totals after each mutation.
3. Save manual/gold/silver zakat profiles, verify haul/no-haul/threshold conditions, snapshot history, link payment and verify paid/remaining.
4. Create portfolio/holding, buy/sell, manual quote, incomplete quote state, uncertain and failed ratio screening. Confirm no cash movement or certification claims.
5. Save/update/delete/filter sadaqah and compare server summary; approved cause directory/intention; labeled approved sponsor placement only.
6. Enable advisor consent, send/read/reload/select/new/delete conversations; disable consent; test provider unavailable and preserve draft.
7. Check 320px and desktop layouts, keyboard focus, empty/error/pending states, unauthorized ownership denial and reload persistence.

Known limits: drafts are in memory and intentionally lost at reload/logout; no mutation idempotency key contract; separate browser tabs are not coordinated for cookie rotation. Preference controls do not provide translated UI or FX. No live banking/prices/payments/brokerage/religious certification is supplied.

## Supplement: goals, reset links and independent-review corrections

- `npm test`: **46/46 passing**, including 15 additional regressions for this supplement.
- `npm run build`: passed; JS 213.90 kB / 66.29 kB gzip; CSS unchanged at 30.97 kB / 7.28 kB gzip.
- `git diff --check`: passed. Supplemental Impeccable detector: `[]`.
- Added charitable goals CRUD, server-reported progress and paginated manual contribution history in Give. Decimal amounts remain strings; goals never transfer money or create donation receipts.
- Added separate silver input/default/type; gold label now refers only to gold. Tests load a nonzero silver profile, edit gold independently and verify missing legacy silver defaults to zero. Final backend schema does not support separate savings/other assets; savings stay in cash/bank balances.
- Reset URL `?token=` is consumed once before React mounts and removed via `history.replaceState`, preserving unrelated query/hash/history state. The in-memory reset form opens directly, including when a refresh cookie exists. Successful reset clears token/form session state. No persistent browser storage is used.
- Addressed reviewer P1 account-switch race: request generation is checked before accepting original/retry responses and before retrying a 401. Four tests cover delayed success/401 from account A after switching to B, including already-started retries; old work cannot return data, replay under B or clear B's session.
- Removed the public-request exemption from account deletion. Tests cover access expiry -> refresh -> successful DELETE and wrong-password rejection without refresh/session loss.
- Payment-history choices now fetch all pages independently of visible history pagination. Tests cover page changes without losing selection and reject missing/currency-mismatched selections; unavailable selected calculations stay visibly labeled rather than silently appearing unlinked.
- Sponsored placements report visible impressions and link clicks through the API. An IntersectionObserver plus hidden-screen/document-visibility checks avoids counting mounted-but-hidden screens; tests cover visibility, offscreen state, cleanup, deduplication and event payloads. Unsupported observation or analytics errors do not block financial workflows.

No servers were started and no parent checkout files were edited for this supplement. Authenticated browser/E2E rechecks and independent re-review belong to the parent orchestration gate; unit transport/visibility tests are not a claim of live browser validation.

## Final backend-enhancement UI delta

The final backend now supports separate `savings`/`other` assets and configurable `gold_nisab_grams`/`silver_nisab_grams`, superseding the earlier supplement's unsupported-field note. Added independent inputs with zero/default-weight migration for older profiles, preserving exact six-decimal strings. Copy warns against counting savings again in cash. Metal-method options no longer imply fixed weights.

Added server-authoritative monthly savings rate (null means no income, not zero) and expense-category values, with wrapping for long category labels. Holdings display `needs_reevaluation`; an expandable, paginated history loads dated screening assessments, sources, methodology, missing/failed checks and disclaimers.

Validation: **51/51 tests pass** (five additional regression tests plus extended decimal payload coverage); production build passes (JS 216.90 kB / 66.90 kB gzip, CSS 31.01 kB / 7.28 kB gzip); diff whitespace check passes; mechanical UI detector returns `[]`. No server started. Parent owns final authenticated browser checks and review.
