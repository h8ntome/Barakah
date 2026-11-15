## Review
- **Correct:** Demo isolation/reset and expiry checks are owner-scoped (`backend/app/demo.py:15–65`, `backend/app/security.py:66–111`). Giving corrections lock affected records; portfolio reversals restore exact snapshots and reject legacy/non-latest trades (`backend/app/giving.py:76–96,252–277`, `backend/app/portfolio.py:175–235`). AI sends return unavailable without inference or persistence (`backend/app/ai.py:34–36`, `backend/app/advisor.py:28–40`).

- **Finding: P2 — Demo reset fails after access-token expiry.** `barakah-ui/src/services/index.js:29` uses `authenticate()`, which calls transport directly without the refresh/retry behavior of `request()` (`barakah-ui/src/services/httpClient.js:114–160`). Access tokens expire after 15 minutes (`backend/app/security.py:110`).
  - **Reproduction:** Start a demo, leave Settings idle for over 15 minutes, then select **Reset demo data**. The reset returns 401; repeated clicks remain unsuccessful until another authenticated request or reload refreshes the session.
  - **Smallest fix:** Give authenticated session-replacement requests the existing 401 refresh/retry behavior, then accept the replacement session. Add a client regression test.

- **Verification limits:** Reviewed the supplied baseline-to-current diff, current source, relevant tests, and uncommitted test changes. No tests executed or services/data mutated. SQLite/PostgreSQL 113-pass results are supervisor-reported; final integrated browser results remain unchecked.

- **Merge verdict: OK with notes.** No concrete P0/P1 regressions found in the reviewed scope.