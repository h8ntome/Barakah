> **Historical pre-release report — not current release status or approval.** This document describes the earlier unavailable-AI build/export. Local AI is now connected, advice remains unverified, and public AI remains unavailable. See [FINAL_RELEASE.md](FINAL_RELEASE.md) and [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md) for the current film. Original findings below are preserved, not reasserted.

# Demo workflow results

Executed 15 November 2026 against **127.0.0.1:8095**, a dedicated SQLite database and separately built frontend. No mocks/interceptions or production records.

| Operation | Result / evidence |
|---|---|
| Health and database schema | `/api/v1/health` 200, ready/database available |
| Demo authentication | `/api/v1/auth/demo` 201; real UI Try Demo; `login.mp4` |
| Profile | Settings saved Amina Rahman; refresh retained name |
| Dashboard | $23,500 assets; $4,500 income / $2,850 expenses / $1,650 surplus |
| Date interaction | October income/expenses $4,200/$4,200; November restored $4,500/$2,850 |
| Spending and transactions | Actual category progress indicators, Transactions selection captured |
| Zakat calculate | Actual Save and calculate zakat, server-success message; $375 estimate |
| Zakat snapshot | Actual Save calculation to history, “Calculation snapshot saved.” |
| Giving history | Actual Sadaqah history expanded; $125 across two fictional records |
| Investments | $8,500 manual portfolio, holdings, allocations, educational Learn tab |
| Assistant | Preferred real Hajj/savings question submitted through real UI; HTTP **503**, `ai_unavailable`. Explicit unavailable notice, draft retained. **No inference happened.** |
| No phantom persistence | Separate authenticated isolated API check returned no conversations after failed send; `verified-evidence.json` |
| Refresh persistence | Demo profile and $23,500 asset total persisted |
| Browser JavaScript errors | None reported in successful final capture session |
| Failed network responses | Expected advisor 503 only; no unexpected >=400 response in capture network log |
| Backend suite | 113 passed; one deprecation warning |
| Frontend suite | 64 passed |
| Build | Existing frontend compiled successfully into dedicated `.runtime/app-dist` |

`browser-network.txt` contains URL/method/status evidence, not request credentials or cookies. Console/error files are empty because no JavaScript exceptions or console output were reported; this does not erase the intentional failed advisor network request.

## Capture iterations

The initial Remotion-bundled FFmpeg could not encode agent-browser recording: it is a limited media build, so a standard Homebrew FFmpeg was installed for capture and QA. Rendering still uses Remotion's own media/browser machinery. The first date-filter rehearsal exposed a browser-automation limitation: `fill` on `input[type=month]` produced an empty native input. The final script uses the native input value setter plus bubbling input/change events, which triggered genuine React/API updates and asserted the returned totals. No displayed data or API responses were rewritten. The completed capture passed all assertions; partial rehearsal files were superseded only in the capture assets folder.

## Not tested in this production

Live model inference (not implemented), live market/metal feeds (unconfigured), actual payments/brokerage/bank sync (not supported), public deployment, PostgreSQL execution, deliverable upload permissions, independent scholarly review and held-out-pretraining provenance. These are not claimed as passing.
