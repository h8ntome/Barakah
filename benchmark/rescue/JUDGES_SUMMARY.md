# Barakah — finance tools with honest model evaluation

**This project is a prototype and is not financial advice.**

> Evaluation-mission summary, preserved with its original test counts below. See [current release audit](../../docs/RELEASE_AUDIT.md) for later local AI integration and the final test evidence. The locally prepared one-page PDF is the canonical final form attachment.

### Problem and product

Barakah helps households organize spending, budgets, savings goals, giving and educational zakat estimates. Its authenticated React/FastAPI product uses stored records, owner isolation and Decimal arithmetic. It does not move money, trade securities, fetch live prices or issue religious rulings. [Try the public demo](https://barakah-gamma.vercel.app/).

### Model and approach

We evaluated the approximately 1.73-billion-parameter [LiquidAI/LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B) against the team's [Barakah checkpoint](https://huggingface.co/h8notme/barakah1). The small BF16 model runs locally on an AMD Radeon 8060S/ROCm system. The team reports adaptation primarily on personal-finance dialogues, not exclusive Islamic-finance training. Exact checkpoint-linked training rows, recipe and split provenance remain unavailable.

Both distributed artifacts are full checkpoints; changed candidate weights were verified. Evaluation used pinned revisions, identical questions, prompts, greedy decoding and token budgets. Neither model received calculators or reference answers. We did not retrain, alter weights, delete failures or replace historical evidence.

### What the original evaluation found

On the unchanged 100-question benchmark, **LFM3 scored 36/40 numerical questions (90%); Barakah scored 32/40 (80%)**. Sixty conceptual answers per model remain unreviewed. The four paired regressions include an incorrect expense total; no formatting correction was justified because every numerical answer parsed. The separate historical simple zakat-rule baseline scored **15/15**, versus LFM3's **12/15** on the same subset. We have **not demonstrated a trained-model advantage over that rule**.

### A separate test of the training objective

The **Personal Finance Domain Adaptation Benchmark v1.0** contains 50 newly authored scenarios and 23 numerical probes. Questions, references and numerical scoring were frozen before inference, then screened evidence was preserved. Available-corpus screening covered 27,981 public dialogue records, but cannot establish the actual training lineage or semantic independence.

Both models completed all 50 scenarios. **Barakah passed 9/23 strict numerical-field checks versus LFM3's 5/23**. Formatting failures were 11 versus 18; token-limit responses were 17/50 versus 27/50. This narrower pass-rate improvement does **not** establish better advice, reasoning or safety. This post-comparison evaluation is exploratory, not independent confirmation. Its subjective rubric required a disclosed late correction before either author inspected new answer text or scores; original files were preserved. All human advice-quality ratings remain null. The two benchmarks are not merged into one score.

### Reliability and remaining work

The application's money calculations are deterministic rather than delegated to the model. Fresh checks passed **127 backend tests** (one PostgreSQL-specific test skipped), **64 frontend tests**, the frontend build and **21 public browser checks**. Six additional calculation regressions exercise exact cents, zero income and observed model-error scenarios; these are debugging fixtures, not held-out model evidence.

**Important limitation:** deployed chat is deliberately disconnected. Offline model inference is real, but this is not a working live AI advisor. A later private opt-in integration is now verified separately; the public endpoint is still disconnected. The event's core-AI requirement, rule-baseline advantage and team eligibility need truthful owner/organizer confirmation. Next steps are verified training provenance, blinded qualified review, and safely integrating model explanations around deterministic accounting.

[Full evaluation and limitations](REPORT.md) · [code](https://github.com/h8ntome/Barakah/tree/audit/full-application-fix) · [credits, requirements and submission checklist](SUBMISSION_CHECKLIST.md). Questions, code and protocol review were AI-assisted using Pi; no AI review is represented as expert human adjudication.
