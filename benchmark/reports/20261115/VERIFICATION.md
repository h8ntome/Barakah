# Verification receipt — 2026-11-15

## Executed, not simulated

- Public Barakah snapshot resolved and downloaded on server2; all declared sizes and LFS SHA-256 values checked. Full BF16 model, not an adapter.
- Original and candidate smoke responses were nonempty actual GPU generations. Initial permission failures are preserved separately; no fallback answer was used.
- Both full runs completed **100/100 successful answers**, zero inference failures, exact frozen question order and IDs. Raw JSONL records and metadata are retained.
- Frozen dataset SHA-256 matches `c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb`.
- Identical modeling source and chat-template bytes; all 100 rendered prompts and input token sequences match. Post-run comparison confirms identical vocabularies/special-token maps, and **116/286 changed weight tensors**.
- Both final processed files have the same scorer-source hash. Numerical grading rules were not changed. Result: **36/40 original; 32/40 Barakah; zero improvements, four regressions**.
- Historical baseline metadata/raw/processed provenance validated. Its original records, rule-based comparison, charts and reports were not overwritten.
- Remote transfer manifest verifies **28 new server-generated files**. Historical transfer manifest still verifies **16 files**.

## Tests and artifact checks

`/tmp/barakah-benchmark-venv/bin/python -m pytest benchmark/tests -q`

**73 passed.** This includes the original 44 tests plus checkpoint resolution/pinning,
full/adapter detection, fail-closed adapter loading, changed-file rejection, frozen
checksums, conflicting resume records, missing metrics, all-error scoring, paired
statistics/configuration/hardware checks, and actual saved-result chart/dashboard/report
integration. Synthetic test fixtures remain in pytest temporary directories; they are
never benchmark evidence.

`validate_paired_artifacts.py` independently reconstructs the paired data/statistics,
checks processed input hashes, chart values and denominators, all 100 dashboard pairs,
10 PNG/10 SVG outputs, local links, and the archived evaluated source hash. PNG exports
are **2400×1350**. CSV/JSON chart data and all paired responses are provided.

The artifact integrity manifest is `results/comparisons/20261115/artifact_integrity.json`.
It is generated after final publication checks, excludes itself, and can be verified
using REPRODUCIBILITY.md. `git diff --check` passes.

## Browser verification

`bash benchmark/tests/check_dashboard.sh` passed against the actual offline HTML:
- outcome filter: four regressions; category intersection: three budgeting regressions;
  difficult intersection: one budgeting regression;
- empty search and reset;
- 25 investing questions show **no numerical score**, not zero correctness;
- chart selector updates the image and corresponding export links;
- BUDGET_006 expands both saved responses;
- 100 question pairs present; images loaded;
- no horizontal overflow at 1440px desktop or 390px mobile;
- separate blinded page contains 60 question pairs.

Receipts: `results/comparisons/20261115/browser_checks_final_verified.log` and
`visuals/20261115/verification/`. Earlier browser attempts did not count as passes:
one expired session opened about:blank, one test expected two difficult budgeting
regressions instead of the actual one, and one viewport transition required explicitly
scrolling to the reset control. The initial saved browser log preserves the viewport
failure; the final receipt above supersedes it. An actual
select-change listener compatibility issue was corrected and retested.

## Independent review

A fresh-context code reviewer identified CPU-frequency comparison and null-truncation
failure handling issues; both were fixed and regression-tested. It confirmed all three
reported issues resolved, including missing-metric rendering. Its review inspected
code and test definitions; the parent executed the tests.

The specialized Impeccable finish-review agent was not registered and did not launch.
A registered read-only reviewer performed the visual review instead: **SHIP / OK** for
the provided desktop/mobile/response screenshots and category/matrix charts. This is
presentation review, not expert finance/religion review. Its scope did not visually
cover every keyboard-focus state or the blinded page. The mobile opening screenshot
ends before the second model's score; that content is present lower down the page.

The design detector reported inherited benchmark palette/radius advisories, the
explicitly requested gold accent, and apparent typography parsing warnings. Two
heading-order findings were corrected before final browser captures. Existing app
DESIGN.md and application code were not changed.

## Remaining scientific and operational limits

No qualified conceptual adjudication; no complete training corpus or exact training
base revision; training leakage not ruled out; shared-server single-pass timing rather
than randomized repeated trials; candidate/base license declaration mismatch. No broad
quality, decoder-speedup or religious-certification claim is supported.

No commit/push was made because no applicable workflow authorization was found.
The pre-existing untracked `demo-video/` remains untouched. Exact final working-tree
status is saved in `results/comparisons/20261115/git_status.txt`.
