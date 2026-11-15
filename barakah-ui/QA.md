# Connected frontend validation

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
