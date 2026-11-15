# Security verification

Checks below were executed in the backend/API and frontend suites, plus local Chromium flows. This is not a claim of a penetration test or certification.

| Boundary | Verified behavior |
|---|---|
| Authentication | Argon2id password hashes; mass-assigned admin role rejected; malformed/expired access tokens denied; access tokens retained only in frontend memory |
| Sessions | Hashed refresh/reset tokens; refresh rotation and concurrent reuse handling; CSRF and trusted Origin checks; logout/password change/reset revoke sessions |
| Reset | Generic request response, expiring single-use token, development outbox file permissions, mocked SMTP STARTTLS flow; actual browser fragment autofill/scrubbing/reset/login |
| Ownership | Cross-user denial/empty reads for accounts, ledger, budgets, Zakat history/payments, giving/goals, portfolios/trades/screening history and conversations |
| Admin | Ordinary users cannot administer causes/ads; only approved active in-window contextual ads served |
| Money | Negative/nonfinite/unsupported precision values rejected; exact Decimal boundary calculations; no cross-currency transfer or silent FX; concurrent overdraft checks and transactional reversals |
| Privacy/errors | Validation does not echo input; SQL parameters hidden; database failures sanitized; private API responses no-store; reset fragments excluded from HTTP request URLs |
| AI | Consent required, opt-in context off by default, owner-only aggregates without raw descriptions or other users; bounded input/output/history/total deadline; local redirects/proxies refused; provider failures rollback chat |
| Browser sessions | Delayed responses/retries cannot cross account generations; account deletion can refresh expired access; logout protects workspace; no automatic write replay |
| Advertising | Financial/chat context not used for targeting; actual visible impression/click verified; explicit sponsored/non-endorsement label |
| Dependencies | Final npm audit and installed-environment pip-audit report zero known vulnerabilities after upgrades |

## Operational limits

- Development HTTP cookies are not Secure. Production configuration must enforce HTTPS, secure cookies, strong secrets and exact origins. Never expose the private reset outbox.
- Rate limits are per process; add trusted edge/distributed enforcement before scaling. Ad counts can be repeated by clients and are not billing-grade.
- Manual/local inputs are not independent financial, religious or charity verification. Inference guardrails and disclaimers are not a guarantee of model correctness or prompt-injection immunity.
- The small load test covers readiness, not heavy finance/advisor traffic. A synchronous advisor call holds a bounded database transaction; test throughput before scale.
- No public SMTP, production ingress, restore drill, external identity service or live inference deployment was exercised. No secrets, database files, model weights, private notifications or raw request logs were added to Git.
