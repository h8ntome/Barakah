# Repairs and decisions

## Authentication and launch
- Preserve Argon2id, rotating HttpOnly refresh cookies, CSRF and explicit origins.
- Added clear duplicate-email feedback, field-name-only validation errors (never input values), malformed/non-JSON API response handling, and a single-origin local launcher with the real built frontend and backend.
- Existing validation test incorrectly forbade the literal word `password`, rather than checking that the password value was not echoed. Updated that assertion to forbid the submitted value, retaining the security intent while permitting useful field-name feedback. This is an intentional test-contract correction, not removal of validation coverage.
- New demo test initially compared Decimal string scale instead of numeric value and accidentally used a 12-character password as an invalid example. Corrected those test inputs/assertions.

## Demo
- Each Try Demo creates a unique non-admin owner, random unusable-to-judge password, 24-hour expiry and normal database-owned records. Reset deletes only the authenticated demo owner and replaces it atomically. Expired demos cannot authenticate and are cleaned in bounded batches on new demo starts.
- Fictional template: income $4,500, expenses $2,850, savings $12,000, portfolio cost/manual valuation $8,500, eligible wealth $15,000 and zakat $375 under explicitly fictional threshold/attested haul. Hajj goal $5,000 with $1,250 contributed. No real payment or verified halal screening is implied.
