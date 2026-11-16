# Training provenance correction — 16 November 2026 UTC

**The submitted checkpoint's training dataset is now identified, not merely a candidate corpus.** This additive investigation supersedes earlier statements that the exact dataset, base revision and training method were unknown. Earlier scoped searches and frozen evidence remain historical records; no benchmark answers, scores, frozen inputs or weights were changed, and no inference or training was rerun.

## Verified chain

1. Four persisted Unsloth Studio LFM3 run records select **[Azfarhashmi/adaption-personal-finance-advice-dialogues](https://huggingface.co/datasets/Azfarhashmi/adaption-personal-finance-advice-dialogues/tree/3dd7f33149d6cbf4ab9115f76242851506929b9d)** at revision `3dd7f33149d6cbf4ab9115f76242851506929b9d`, subset `default`, Hub split `train`. The cached `data/train_0.jsonl` contains **27,981 records**, 354,098,432 bytes; its SHA256 matches the pinned public Hub LFS object.
2. Saved configs select **LiquidAI/LFM3-1.7B** at `1da06bec6a819da10b54c67e5c90972b46d81871`. Unsloth trained LoRA (`r=16`, alpha 16, no 4-bit loading), batch 2, accumulation 4, learning rate 0.0002, seed 3407, maximum sequence length 8192, packing off. Configured mapping: `enhanced_prompt → user`, `enhanced_completion → assistant`, `original_context → system`; format `auto`, completion-only training enabled. Both enhanced columns are strings in every record; original_context is a string in 11,222 records and null in 16,759. These are persisted configuration and input-schema facts, not a recovered per-token processing trace.
3. Latest run `job_20261115_114633_01105c08` stopped at **4413/6996 steps**. Saved trainer state records epoch **1.2615967407619184**. Two epochs were planned, **not completed**. The root adapter and checkpoint-4413 adapter have identical SHA256. Dataset cardinality is not a claim that 27,981 unique examples were consumed to completion.
4. `export_metadata.json` names that run family's output directory as `source_checkpoint` and LFM3 as the base. The actual exported full `model.safetensors` is 3,457,635,448 bytes, SHA256 `0d09d744e4ed20c7ecd73968dc127e909ae524d642967f772c09de65779bde22`: **exactly the submitted [h8notme/barakah1 revision](https://huggingface.co/h8notme/barakah1/tree/912a5697cf9d85adf065ee512f509cfa236459d4)** and its public pinned LFS object. The export is a full checkpoint, not a separately distributed adapter. No merge was performed during this investigation.

[Sanitized evidence, hashes and selected configuration](evidence/training-provenance-20261116.json). Private discovery receipts retain the exact read-only commands and source paths; no credentials, training corpus or weights are redistributed.

## Credits and limits

Credit **Azfarhashmi** for publishing the dataset. Its [pinned dataset card](https://huggingface.co/datasets/Azfarhashmi/adaption-personal-finance-advice-dialogues/raw/3dd7f33149d6cbf4ab9115f76242851506929b9d/README.md) says it was remastered using **Adaption's Adaptive Data platform**. Credit **Unsloth** for training and **LiquidAI** for the base model. The card's quality claims are publisher claims, not our expert validation.

- **Licensing is unresolved:** the dataset card specifies `license: []` and `source_datasets: original`, without identifying an upstream source or granting a license. The candidate's Apache-2.0 card does not resolve inherited LFM Open License v1.0 obligations. Dataset identity does not establish a complete upstream rights chain.
- **Evaluation independence is unresolved:** `eval_split=null`, no local datasets/evaluation datasets and no slicing were configured. Within the selected Hub `train` file, row-level `split` labels are **train 7,825 / test 1,721 / val 1,676 / missing 16,759**. Those labels are not separately withheld Hub splits and do not establish a clean holdout. The existing exploratory lexical overlap screen is narrow evidence, not semantic or pretraining-contamination clearance.
- **Expert quality is unresolved:** 60 conceptual responses per model remain unreviewed. The matched scores remain rules/original/candidate **15/15, 12/15, 11/15** on Zakat and original/candidate **36/40, 32/40** overall, tolerance 0.01. Identifying the dataset does not turn regression into superiority or certify financial/religious advice.

The frozen `personal_finance/PROVENANCE.md` intentionally retains its earlier uncertainty; use this dated correction for current lineage claims. No frozen manifest is rewritten to conceal the historical state.

This is a documentation/evidence correction. Production runtime remains commit `9ed49370a7f6ab3f3b21b26a1e87c90e12b71b29`; no redeployment is required or claimed.

**This project is a prototype and is not financial advice.** Islamic finance is educational, not religious certification.
