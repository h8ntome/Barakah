# Real frontend/backend integration evidence

The existing emerald/mint design, typography, desktop shell, mobile navigation and five primary destinations remain intact. Chromium interacted with React on port 5173 and FastAPI on port 8000, backed by native PostgreSQL. No application mock adapter was used; the advisor itself was intentionally configured in its visibly labelled mock-provider mode.

## Browser journey: 29 assertions

Registration and empty workspace → cash account → blocked-network transaction/draft-preserving retry → income/expense → category budget → Zakat calculation/history/partial payment → Sadaqah record → giving goal/contribution → portfolio/holding/buy trade → dated manual quote → uncertain screening → mock chat with expressly opted-in verified totals → reload/history → logout/protected navigation → login/persisted balances → quoted net worth → saved custom screening validity → 390px overflow check.

Known fictional values: opening cash 1,000; income 4,000; expense 200; cash balance 4,800; budget 500 with 300 remaining; eligible Zakat base 10,000 and manual Nisab 6,800 giving 250 due, 50 recorded paid, 200 remaining; ten shares at 20 cost and dated quote 21 yield 210 value/10 unrealized gain; dashboard net worth 5,010. No live prices or actual money movement are implied.

## Additional live checks

- Password reset: four assertions cover generic request, private outbox token in fragment, immediate URL scrubbing, successful password change and browser sign-in with new password. The isolated reset user and notification were deleted afterward.
- Sponsored placement: an approved fictional dashboard campaign was provisioned through admin API after trusted test-role setup. The actual rendered placement was scrolled into view and its link clicked. Database query recorded `impression=1`, `click=1`; campaign was then disabled. This is not a claim of production fraud-proof analytics.
- Demo script: seeded a unique fictional account, verified finance/Zakat/advisor data through the API and deleted that isolated account.
- Readiness: migrated schema reports ready; automated regressions return unavailable for absent database tables or an older migration head.

## Inspected screenshots

- [Finance](screenshots/01-finance.png)
- [Zakat history and partial payment](screenshots/02-zakat.png)
- [Manual investment valuation](screenshots/03-investments.png)
- [Mock advisor and verified monthly totals](screenshots/04-chat.png)
- [390px mobile dashboard](screenshots/05-mobile.png)
- [Clearly labelled fictional sponsored placement](screenshots/06-sponsored.png)
- [Password reset confirmation, with no token visible](screenshots/07-reset-confirmed.png)

All captured financial values and identities are fictional test data. Screenshots prove the inspected states, not every browser, keyboard, screen-reader or future deployment configuration. See [raw outputs](evidence/) and [known limitations](feature-coverage.md).
