# Training-data leakage investigation — 2026-11-15

## Confirmed
- Frozen benchmark bytes match SHA-256
  c8a9636cc9ad96cbfb1049168227a23e5fc213ce245264be44984667578801fb.
- 100 questions, 100 unique questions after Unicode NFKC, case folding and whitespace
  collapse. This checks internal exact duplicates, **not training overlap**.
- Public checkpoint h8notme/barakah1 at
  912a5697cf9d85adf065ee512f509cfa236459d4 has 11 files: model/tokenizer/code/config
  and a short model card. No training dataset, dataset identifier, manifest or training
  log is published there. The card attributes training to Unsloth/TRL.
- An unauthenticated Hugging Face Hub query for public datasets by author h8notme
  returned an empty list. This does not exclude private, differently named or external data.
- Local scoped repository searches found benchmark/training-boundary documentation,
  not a training corpus linked to this checkpoint.
- A read-only scout checked bounded paths under server2's existing AI and benchmark
  directories. It stopped at an unrelated permission-denied recovery directory.
  Parent inspection confirmed Unsloth process visibility but container/root and Docker
  access were denied. No privileges, permissions or workloads were changed.

## Not established
The exact training corpus, complete training-stage coverage, train/evaluation split,
training base revision, and checkpoint-to-dataset linkage remain unknown.
**Zero cross-corpus pairs were compared. Exact-match and near-duplicate leakage
counts are unavailable, not zero. Leakage has not been ruled out.**

## Required follow-up
Obtain authorized training manifests and datasets for every training stage, with raw
file hashes, dataset revisions, split membership and linkage to this checkpoint.
Compare public evaluation questions against user prompts and embedded prompts in
complete training records:
- exact bytes;
- NFKC/casefold/whitespace-normalized matches;
- punctuation-normalized matches;
- token-set Jaccard >=0.80 and character similarity >=0.90 candidates;
- number-masked structural templates, separately from exact-example overlap.

Review candidates manually, preserving differing numbers and reference prose.
Those thresholds are proposed and have **not** been executed as a corpus audit.
Report candidate counts and question IDs even if overlap harms the headline result.
If significant overlap is found, retain this benchmark and add an independently
authored private holdout; never remove or rewrite leaked items to conceal overlap.
