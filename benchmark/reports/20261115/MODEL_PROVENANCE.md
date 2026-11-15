# Model provenance — 2026-11-15

## Artifact identity
| | Original | Barakah |
|---|---|---|
| Hugging Face repository | LiquidAI/LFM3-1.7B | h8notme/barakah1 |
| Immutable revision | `1da06bec6a819da10b54c67e5c90972b46d81871` | `912a5697cf9d85adf065ee512f509cfa236459d4` |
| Public without authentication | true | true |
| Artifact type | Full model | Full model, not PEFT adapter |
| Architecture | Lfm3ForCausalLM | Lfm3ForCausalLM |
| Stored weight dtype | BF16 | BF16 |
| Stored parameter elements | 1728801536 | 1728801536 |
| Weight bytes | 3457635448 | 3457635448 |
| Weight SHA-256 | `135922caef64e81e52af88ede8b7c3ddaa9d6da220a9737fb3065275dbfb4330` | `0d09d744e4ed20c7ecd73968dc127e909ae524d642967f772c09de65779bde22` |

Both contain a complete single safetensors weight file with 286 tensors. All Hub LFS
SHA-256 values and declared file sizes were checked; safetensors headers were opened.
All other downloaded files were also SHA-256 hashed. Inventory:
[original](../../results/hardware/original_checkpoint.json),
[Barakah](../../results/hardware/barakah1_checkpoint.json).

The actual loaded parameter counts and generation configurations are in run metadata.
No quantization, PEFT attachment, merge operation or model substitution was performed
during evaluation. Different full weight hashes establish distinct downloaded artifacts;
real generated outputs establish successful inference. A post-inference CPU comparison
checked every corresponding tensor with torch.equal: **116/286 tensors differ** and
170 are unchanged. Tokenizer vocabularies and special-token maps are identical.
See `results/hardware/weight_difference.json`. This confirms changed tensor values,
not merely a reserialized weight file; it does not reconstruct the training process.

## Base relationship and training claims
The candidate card declares `base_model: LiquidAI/LFM3-1.7B` and attributes training to
Unsloth/TRL. It does not pin the training base revision or identify a training corpus,
adapter configuration, hyperparameters or training log. Its heading says “16-bit (FP16)”,
but safetensors inspection confirms **BF16**; measured tensor dtype takes precedence.
The release is a full checkpoint; whether an upstream training process used and merged
LoRA cannot be established from this artifact. Do not claim identical-base-revision
fine-tuning: compatibility with the intended baseline is verified, training lineage at
that exact commit is not.

## Snapshots and loading
- Original: `/home/hadi/.cache/huggingface/hub/models--LiquidAI--LFM3-1.7B/snapshots/1da06bec6a819da10b54c67e5c90972b46d81871`
- Barakah: `/home/hadi/ai/hf-barakah-cache/models--h8notme--barakah1/snapshots/912a5697cf9d85adf065ee512f509cfa236459d4`

`checkpoint.py` resolves the Hub commit before snapshot_download, preserves the model
card/config, verifies all declared files and LFS hashes, and records absolute locations.
`run_benchmark.py --checkpoint-manifest ...` rehashes every listed file before loading,
requires manifest repository/revision agreement, and rejects an adapter rather than
silently evaluating an unchanged base. This experiment did not require PEFT support.

AutoTokenizer and AutoModelForCausalLM load the corresponding immutable local snapshot
with trust_remote_code=true, dtype=bfloat16 and attn_implementation=sdpa, followed by
GPU transfer and eval(). The three required custom source files are byte-identical
between these snapshots. Baseline code was already used in the historical run; no
additional candidate-specific executable model code was introduced.

## Tokenizer and chat template
Each checkpoint's own tokenizer is used. The tokenizer.json hashes differ; input
equivalence was tested rather than assumed. All 100 rendered prompts and token-ID
sequences match exactly. The shared chat-template file SHA-256 is
`f45005c50cd2a97329722bf3a2dee9f16c04cdf825a589b280fb7e99e6827818`.
Metadata records the effective tokenizer chat template and its string hash separately.
See [compatibility evidence](../../results/hardware/checkpoint_compatibility.json).

## Runtime and operational warnings
Working interpreter: `/home/hadi/homefinance-benchmark-lfm3/.venv/bin/python`.
No system package or shared environment was changed. Full package inventories are
`results/hardware/matched_inference_environment.txt` and
`matched_analysis_environment.txt`.

The default Hugging Face Hub/Xet/custom-module cache has root-owned directories.
Initial download and candidate smoke attempts failed on permissions. These failures
and logs are preserved. User-owned `/home/hadi/ai/hf-barakah-cache` was used instead;
HF_XET_CACHE and HF_MODULES_CACHE were redirected, not system permissions.
The successful baseline used its pre-existing custom-module cache; the candidate used
the new module cache. Modeling code is identical, but cold loading time is descriptive,
not a cache-controlled model loading speedup.

ROCm emits a libnuma/rocSHMEM diagnostic; actual BF16 GPU generation succeeds.
The candidate generation config sets max_length=262144 and emits a warning that the
explicit 24-token warm-up / 384-token evaluation max_new_tokens takes precedence.
The warning is retained; no larger candidate output budget was used.

## Licenses
Original distributes **LFM Open License v1.0** in its LICENSE file.
Candidate model-card metadata declares **Apache-2.0**, but no separate LICENSE is
present in its 11-file repository. That declaration does not resolve upstream license
obligations. Obtain owner/legal clarification before redistribution or commercial use.
No large model weights or credentials are included in Git.

## File inventories

### Original

| File | Bytes | SHA-256 |
|---|---:|---|
| .eval_results/LFM3-1.7B.yaml | 1553 | `3e162ea4fdde47af47e1050b40d9b6aa516baa59cfd935217c23079b4c15c0be` |
| .eval_results/ifbench.yaml | 192 | `63bfe58f450590722ac86fc43c97a8388d2a0ac077910719ca39f29736a4575c` |
| .gitattributes | 1838 | `98cd74542392d7df88b3ea5c23e39bf347e44499d3a5250744c6f07cb5b1c64f` |
| LICENSE | 10574 | `4d28ca14dedc0b3d0fcc2b3339f0e79931faa33874f3d24f522183a8fc70068c` |
| README.md | 55086 | `63ef157d747e4fd77376a6eca0d7177bbeb4a2db3c9f5baacfd6afaf5a338e55` |
| assets/icons/api.svg | 304 | `6a4bf6961897b9f33582cc1fdf580c24c02436f8edcd1c42c33f11e4fa1db7bd` |
| assets/icons/blog.svg | 329 | `ad444704791f705ea53d1293a9e86b688cb5f4837a8b74dbe342eced1caba895` |
| assets/icons/docs.svg | 347 | `2f3ad60851ac6726df7e0409038fcd45722f3c4b69539bf16cd797477be8568e` |
| assets/icons/try.svg | 317 | `ba010a64fa3d2d71d91bd14c7ea948f9189bf2b9c08069319e27634da00645ee` |
| assets/lfm3-edge-inference.webp | 213860 | `ac73ebf33a4ea9aa3191d64f28d10a3ed51531dfa5442390071b876ae1b37ea4` |
| assets/lfm3-gpu-throughput-b300.png | 85302 | `cb378a251ef1234e7a7251b74952db0e7ea39d17c93cf6300dc3229093e342eb` |
| assets/lfm3-post-training-recipe.webp | 19342 | `27d21292d1e8998a3ca52dad11f6905a74b60f367ae167e56e4fba3381bef477` |
| assets/lfm3-pre-training-recipe.webp | 28860 | `1ecdb5082691ddcfaa14426cd3437f8948e3adb220c72616af4117eb51246b2f` |
| assets/liquid-ai-banner.webp | 38172 | `30dbbfb9f1b412462ef8f690e95d490100b04487a4f534ac09a92f636f734196` |
| chat_template.jinja | 12129 | `f45005c50cd2a97329722bf3a2dee9f16c04cdf825a589b280fb7e99e6827818` |
| config.json | 1454 | `8c6ae8b8f6d88c87cfb98cf4b5e34e943d0ee07e24215c4121b3159a46e1399d` |
| configuration_lfm3.py | 6113 | `176cced35657aedfea7d7002221360582d1c05fcaca882c21508bc3a73b282e5` |
| generation_config.json | 328 | `0095ba7158e938b1e2d3082d412f00d8be85e42cbbd7608b63866f7a081cf270` |
| lfm3_conv.py | 8532 | `80d4a985382a22774212759248a6b4c737bfbf9c2a47b3dd7f797dda748e4bb4` |
| model.safetensors | 3457635448 | `135922caef64e81e52af88ede8b7c3ddaa9d6da220a9737fb3065275dbfb4330` |
| modeling_lfm3.py | 42359 | `e8cd5254ea99ce6bd731b57b10908c2e8b5010ce8315341f895a38484885eeab` |
| special_tokens_map.json | 92 | `7946f864cbfb62a1b041bda937244210a1a87f4a6cab3a48b791131b2cd57f88` |
| tokenizer.json | 17908635 | `7e226e34bface23ccf6e495d157bf77186c1c30a7659880e1a8994db528c3701` |
| tokenizer_config.json | 1545 | `bf028f813efc6137bc07ed045cafe71820df9a5e26a38e39954706ed1e30a457` |

### Barakah

| File | Bytes | SHA-256 |
|---|---:|---|
| .gitattributes | 1570 | `34448b82c17d60fec9b65b1f093c115ddbaadc04beb1b0140b6bfed2e012a930` |
| README.md | 571 | `2c98f593d0412a5be0647e0c8b5ac76da9cb93caf67d1450d8bd6688789a9931` |
| chat_template.jinja | 12129 | `f45005c50cd2a97329722bf3a2dee9f16c04cdf825a589b280fb7e99e6827818` |
| config.json | 1574 | `70b9c4294f89335d6141883a77bc03311e1e0ad51db78d9cc5c7822775443276` |
| configuration_lfm3.py | 6113 | `176cced35657aedfea7d7002221360582d1c05fcaca882c21508bc3a73b282e5` |
| generation_config.json | 352 | `8a5ac17ef9b625e6f6b171d6974930ec4327b48bc713366e0cdf681825f173bf` |
| lfm3_conv.py | 8532 | `80d4a985382a22774212759248a6b4c737bfbf9c2a47b3dd7f797dda748e4bb4` |
| model.safetensors | 3457635448 | `0d09d744e4ed20c7ecd73968dc127e909ae524d642967f772c09de65779bde22` |
| modeling_lfm3.py | 42359 | `e8cd5254ea99ce6bd731b57b10908c2e8b5010ce8315341f895a38484885eeab` |
| tokenizer.json | 17908634 | `41927bd314d17d7d7fadb44e10cd0919f7b71528d7741596d8cbd15c6945ec44` |
| tokenizer_config.json | 40454 | `603b9f41eaa293b8f636c849537841b2c107fa7369007b7cef117e7818be72e5` |
