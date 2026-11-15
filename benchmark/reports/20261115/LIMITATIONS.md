# Limitations

- Only **40 numerical questions** are automatically scored. The **60 conceptual
  questions per model (120 responses)** need qualified human review. There is no
  justified overall 100-question accuracy, verified hallucination rate or verified
  unsafe-response rate yet.
- Institutional reference checking is not expert validation. This benchmark does
  not establish comprehensive fiqh expertise or religious certification.
- Numerical correctness verifies a final quantity and unit, not surrounding advice.
  Strict terminal-answer formatting can reject mathematically sound prose; any human
  override must be a separate response-bound review, never a raw-output replacement.
- The sample is small, authored and nonrandom. Repeated calculation patterns reduce
  diversity and effective independence; bootstrap intervals and McNemar results are
  exploratory, not population guarantees.
- Training-data overlap has **not been ruled out**. The public model card identifies
  no training dataset or immutable base revision. Accessible scoped discovery found
  no linked corpus; container/other-directory access was denied and not bypassed.
  No cross-corpus exact/near-duplicate check could be completed. This must not be
  presented as a proven clean holdout merely because it is in a separate directory.
- The model card's "fine-tuned from LFM3-1.7B" is uploader attribution, not a recovered
  training log. Exact optimization method, training steps, data, adapter history and
  training base commit remain unverified. The distributed artifact is a full checkpoint.
- Both runs use one shared server and a sequential order (baseline then candidate).
  No unrelated workload was stopped. No randomized repeated timing trials, power
  control or continuous before-to-after telemetry was performed. Timing comparisons
  are matched-environment observations, not guaranteed speedups.
- Output length changes affect total latency. Throughput includes prefill and special
  tokens; it is not decode-only speed. File/tokenizer serialization differs although
  all 100 public input token sequences matched.
- BF16 and warning-only deterministic settings do not guarantee bitwise determinism.
  Historical baseline performance is not substituted for this session's measured baseline.
- No Arabic assessment, live market/nisab data, retrieval, calculators, production
  concurrency, real financial accounts or individualized portfolio advice is tested.
- Financial advice requires appropriate caution and professional review; differing
  religious interpretations must not be collapsed into a fabricated definitive fatwa.
- The candidate card declares Apache-2.0, whereas the base checkpoint distributes the
  LFM Open License v1.0. This mismatch needs owner/legal clarification; do not assume
  the uploader's card overrides upstream obligations.
