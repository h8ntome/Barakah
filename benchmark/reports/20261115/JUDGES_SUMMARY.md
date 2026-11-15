# Barakah AI: what the benchmark actually shows

Barakah is an Islamic personal-finance application. Its AI candidate is a full
fine-tuned checkpoint published by h8notme, attributed to LiquidAI's LFM3-1.7B.
The card credits Unsloth/TRL; the training dataset and exact training recipe are not verified.

## The measured result

**Original: 36/40 (90.0%) → Barakah: 32/40 (80.0%).**

**-10.0 percentage points. 0 improvements. 4 regressions.**

The fine-tuned checkpoint regressed on the measured numerical score. The paired test p-value is 0.1250;
the 95% paired interval is [-20.0, -2.5] percentage points.
Only 40 authored calculations are scored—not all of Islamic finance.

Both models answered the same 100 questions on server2 with the same prompt,
output budget and runtime. All responses, including regressions, are preserved.
Mean generation latency was 4.786s versus
4.520s; throughput was
40.948 versus
40.912 output tokens/s.
These are single shared-server measurements, not guaranteed serving performance.
Output token totals: original 19,599,
Barakah 18,490. Lower average latency alone
is not evidence of a faster decoder; response length matters.
Responses reaching the output cap: 2/100 original,
13/100 Barakah.

## What remains unverified

- 60 conceptual answers per model still need qualified human review.
- No verified hallucination, safety or religious-certification claim is supported.
- Training overlap has not been ruled out; exact training base revision is unknown.
- A full checkpoint is confirmed; a specific LoRA training process is not.

## Open the evidence

- [Interactive dashboard](../../visuals/20261115/html/index.html)
- [Ten presentation charts](../../visuals/20261115/png/)
- [Complete report](BENCHMARK_REPORT.md) and [three demo examples](DEMO_EXAMPLES.md)
- [All 100 paired responses](../../results/comparisons/20261115/questions.csv)
- [Reproduce it](REPRODUCIBILITY.md)

**Bottom line:** the fine-tuned checkpoint regressed on the measured numerical score. This does not establish improved conceptual Islamic-finance quality; those answers are unreviewed, and training overlap and the exact training base revision are unresolved.
