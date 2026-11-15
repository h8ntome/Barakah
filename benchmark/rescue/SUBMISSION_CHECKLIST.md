# Submission readiness — 2026-11-15

**This is a preparation checklist, not a submission receipt.** No form has been submitted by this evaluation mission.

## Official requirements

- [Instructions and submission link](https://highschoolhackathon.org/briefs)
- [Submission form](https://airtable.com/appypCyHN77hElIcS/shrXA5VBFdugmoXl6)
- [FAQ](https://highschoolhackathon.org/faq) · [judging](https://highschoolhackathon.org/judges)
- Official deadline: **2026-11-15 23:59 Eastern = 2026-11-16 04:59 UTC**. Respect an earlier team deadline if applicable. The site recommends submitting an hour early; no late-submission entitlement is implied.
- One person submits for the team. Required: public code, one write-up, Finance track, team identities/emails/schools, credits, project pitch, and truthful rules confirmations.
- Optional video: **at most two minutes**, unlisted YouTube or Drive with anyone-with-link viewing. A local MP4 is not a public video link.
- Required Finance disclaimer: **“This project is a prototype and is not financial advice.”**

The public instructions/form were inspected read-only on 2026-11-15 around 16:09–16:12 UTC by the submission scout. Finance PDF requirements were cross-checked against the previously captured `demo-video/reports/REQUIREMENTS.md`; not every PDF passage was re-extracted during this mission.

## Links to use

| Asset | Link / status |
|---|---|
| Code | https://github.com/h8ntome/Barakah/tree/audit/full-application-fix — use this explicit branch, not the stale default branch |
| Short submission write-up | https://github.com/h8ntome/Barakah/blob/audit/full-application-fix/benchmark/rescue/JUDGES_SUMMARY.md |
| Full technical report | https://github.com/h8ntome/Barakah/blob/audit/full-application-fix/benchmark/rescue/REPORT.md |
| Original model | https://huggingface.co/LiquidAI/LFM3-1.7B |
| Fine-tuned checkpoint | https://huggingface.co/h8notme/barakah1 |
| Public demo | https://barakah-gamma.vercel.app/ — choose Try Demo |
| Original benchmark | https://github.com/h8ntome/Barakah/tree/audit/full-application-fix/benchmark/datasets |
| Separate personal-finance benchmark | https://github.com/h8ntome/Barakah/tree/audit/full-application-fix/personal_finance |
| Historical video | Local `demo-video/output/barakah-demo-final.mp4`, 115.008 seconds; hosting not verified; it predates the new paired evaluation |

New links become available only after the corresponding commit is pushed. Check anonymously before copying into the form. Do not use the historical video as evidence of the latest model results; it correctly shows disconnected chat but its evaluation coverage is older. The video is optional, so do not delay submission to re-render it.

## Owner decisions still required

- [ ] Enter the exact team members, emails, schools and registration details. Never invent them.
- [ ] Confirm high-school eligibility, contributions, permitted build window, and no disallowed pre-existing project extension.
- [ ] Resolve the **core-AI requirement**: the app's accounting works, but its public chat is intentionally disconnected. Offline model inference/evaluation is real and reproducible; it is not live product integration. Do not certify that the deployed tracker alone demonstrates AI doing its main job.
- [ ] Confirm actual fine-tuning dataset/revision/splits and license obligations. The team's description is personal-finance dialogue adaptation; a complete checkpoint-linked training manifest was not supplied.
- [ ] Include all actual model, dataset, tutorial and AI-tool credits. Pi/AI coding assistance must not be represented as solely human-authored implementation.
- [ ] Select one public write-up (the short judges summary links the full evidence), verify every submitted URL, and use the Finance disclaimer above.
- [ ] Submit the form and save the timestamp/confirmation receipt. A Git push is not a hackathon submission.

## Honest pitch

Barakah combines an Islamic personal-finance tracker with a reproducible study of a small language model adapted for financial conversations. We preserve the original benchmark, disclose numerical regressions, and add a separately frozen exploratory personal-finance evaluation. The application uses deterministic Decimal accounting instead of trusting a model with money. The deployed chat is not yet connected; advice quality and scholarly correctness still require independent review.

## Credits and provenance

- Liquid AI: [LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B), LFM Open License v1.0.
- Team-distributed [Barakah checkpoint](https://huggingface.co/h8notme/barakah1); model card credits [Unsloth](https://github.com/unslothai/unsloth) and [TRL](https://github.com/huggingface/trl). These credits do not independently verify the training recipe.
- Candidate dialogue corpus for overlap screening: [Azfarhashmi/adaption-personal-finance-advice-dialogues](https://huggingface.co/datasets/Azfarhashmi/adaption-personal-finance-advice-dialogues). Exact use in this checkpoint is not independently confirmed.
- Evaluation questions: AI-assisted authored synthetic scenarios; construction and limitations recorded in each benchmark's manifest/card. Original reference-source links are in `benchmark/datasets/SOURCE_EVIDENCE.md`.
- Evaluation/runtime: [Transformers](https://github.com/huggingface/transformers), [PyTorch](https://pytorch.org/), [AMD ROCm](https://rocm.docs.amd.com/), Python.
- Product: [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [React](https://react.dev/), [Vite](https://vite.dev/); pinned dependency manifests are in the repository.
- Coding/review/testing assistance: Pi coding agent and AI subagents; [agent-browser](https://github.com/vercel-labs/agent-browser). Team must append any additional tools/tutorials actually used.
- The candidate's Apache-2.0 model-card label does **not** supersede the upstream model license; seek clarification before redistribution/commercial use.
