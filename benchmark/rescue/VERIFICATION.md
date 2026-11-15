# Rescue verification receipt — 2026-11-15

## Measurements accepted

- Original matched runs: 100 responses/model; strict numeric **36/40 vs 32/40**. Rational-arithmetic audit verified all 40 reference values; zero unparseable numeric answers, so no semantic correction was introduced.
- Personal-finance runs: 50 responses/model, zero generation failures; strict labeled numeric fields **5/23 vs 9/23**. Unparseable fields **18 vs 11**; token-cap responses **27 vs 17**. These are not complete-answer advice-quality scores.
- Independent AI acceptance reproduced all 100 saved per-item outcomes and passed all 16 artifact checks. Questions, order, pinned checkpoints, prompts, input tokenization and operative generation settings match.
- All **500 human-rating fields remain null**. The initial subjective-rubric omission and late prospective correction are disclosed. No AI engineering review is presented as qualified human advice adjudication.

## Executed checks

| Check | Result |
|---|---|
| Backend suite | 127 passed; 1 PostgreSQL-specific test skipped |
| Additional calculation regressions | 6 passed, included in the backend total |
| Frontend unit tests | 64 passed |
| Frontend production build | Passed |
| Evaluation tooling suite | 77 passed |
| Personal-finance original + supplementary tests | 6 + 3 passed |
| Fresh public Chromium journey | 21 checks passed |
| Original paired artifact inventory | 122 files verified |
| Original evidence present at mission start | 89 files unchanged |
| Personal-finance frozen inputs/dependencies | 26 hashes verified |
| Worker-delivered personal-finance artifacts | 65 hashes verified |
| Canonical human review | 50 pairs; 500 null ratings; separate identity mapping |

Public-browser test attempts that failed on missing readiness waits are retained in `evidence/public_demo.log` and `public_demo_retry.log`. The corrected run is `public_demo_verified.log`; no model inference was repeated because of these browser-test failures. Its temporary registered user was deleted; synthetic demo workspaces expire automatically.

Code-only staged whitespace checks pass. Generated SVG/HTML and verbatim model-response artifacts contain pre-existing whitespace warnings; their bytes were preserved rather than cosmetically rewritten. The matched artifact manifest still verifies. The three new figures were inspected as images; their values are bound to recorded evidence in `visuals/chart_data.json`.

## Publication scope

The staged-package scan checked 222 substantive files (~7.9 MB), with no high-confidence credential-pattern hits, model weights, private databases, environment files or videos. The later scan receipt, this verification note and the final hash inventory are administrative additions. This is a targeted scan, not a comprehensive security audit.

Only evaluation work, root documentation, six API regression fixtures and the readiness-wait hunks of `tests/e2e/public_demo.py` are included. Concurrent changes to root `.gitignore`, `scripts/demo.py`, `tests/e2e/journey.py`, and the output-directory hunk in `public_demo.py` are left unstaged. Pre-existing `demo-video/` is preserved and excluded.

`personal_finance/REPORT.md` remains the isolated worker's pre-import receipt; `personal_finance/DELIVERY.md` explains the final integration. The final submission inventory hashes **Git-index bytes**, not concurrent unstaged worktree edits.

## Still not done

- No independent human finance/religious review or clean training-lineage confirmation.
- No retraining, weight changes, live AI integration, extra video render/upload or production database migration.
- No hackathon form submission or eligibility/core-AI certification. Team identities, confirmations and an actual submission receipt still require the owner. A pushed commit is not that receipt.
