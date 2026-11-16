# Current provenance correction — 16 November 2026

**The submitted model's actual training dataset and export chain are verified.** [Read the current evidence, full dataset credit, split details and limitations](../docs/TRAINING_PROVENANCE_CORRECTION.md).

`README.md`, `REPORT.md` and `PROVENANCE.md` in this directory are frozen, hash-bound historical evidence. Their earlier claim that the corpus was only a plausible candidate is superseded. They remain byte-identical so the existing freeze and artifact manifests remain valid.

Azfarhashmi's dataset revision `3dd7f33149d6cbf4ab9115f76242851506929b9d` contains 27,981 input records, remastered with Adaption's Adaptive Data platform per its card. Unsloth records select the Hub train split, with no evaluation split or slicing; row-level test/val labels are not held-out evaluation. Training stopped at 4413/6996 steps (1.26 epochs). Dataset/inherited licensing, evaluation independence and expert advice quality remain unresolved. No new inference or benchmark was run.

[Historical measured results](REPORT.md) · [original frozen provenance](PROVENANCE.md) · [original protocol](README.md). Historical results and failures remain unchanged. This project is a prototype and is not financial advice.
