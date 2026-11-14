# Evaluated model card

## Provenance
- Creator and owner of original weights: **Liquid AI**.
- Repository: https://huggingface.co/LiquidAI/LFM3-1.7B
- Revision: `1da06bec6a819da10b54c67e5c90972b46d81871`.
- Instruction-tuned checkpoint; the listed upstream base is LFM3-1.7B-Base, **not** the evaluated artifact.
- Approximately 1.73 billion parameters; BF16 safetensors.
- Architecture described by Liquid AI as tri-hybrid (convolution, sliding and full attention).
- Model license: **LFM Open License v1.0**, official repository LICENSE. Do not infer rights from the Apache notices in modeling source files.
- Source model card: https://huggingface.co/LiquidAI/LFM3-1.7B/blob/1da06bec6a819da10b54c67e5c90972b46d81871/README.md

The download metadata records snapshot path, hashes, size and tensor count. Cached official weights were verified rather than redundantly re-downloaded. The model was loaded and exercised on server2. No weights are included in this repository.

## Evaluated configuration
Transformers 5.20.0, PyTorch 2.12.0+rocm7.14.1 on AMD Radeon 8060S; official pinned custom code with explicit trust, tokenizer and chat template. BF16 execution, SDPA, no quantization, greedy batch-one generation, thinking disabled, 384-token cap, seed 2026. See configuration and raw metadata for exact settings and full template. The local CPU fallback is FP32 and is not the published reference execution.

## Intended use
Educational research and establishing an original-model baseline before Islamic-finance adaptation. Barakah may eventually use a small local model for explanations and conversational support. This evaluation does not implement that integration.

## Not established / out of scope
No qualified religious certification, personalized investment advice, guaranteed returns, autonomous trading, live stock screening, current nisab pricing, Arabic correctness, fraud-proof advice, tool execution or deployment readiness. No adapted model was trained or evaluated.

## Risks
The model can produce plausible but false religious claims, overgeneralize methodologies, make arithmetic errors and miss needed context. A small English authored benchmark does not establish general Islamic finance expertise. Production requires validated financial tools, provenance-aware retrieval, qualified review, privacy and security controls, and ongoing testing beyond this benchmark.

## Authorship boundary
The benchmark code, authored questions and presentation are Barakah evaluation artifacts. They are not Liquid AI-authored benchmarks, endorsements or vendor-reported performance. Original model capabilities and training descriptions are attributed to the official model card; this project reports only its own saved measurements.
