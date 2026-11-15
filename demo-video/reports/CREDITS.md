# Credits and licensing

## Product and evidence

Current release also uses [h8notme/barakah1](https://huggingface.co/h8notme/barakah1), full revision `912a5697cf9d85adf065ee512f509cfa236459d4`, in the actual private local app capture. The foundation model below is the separate offline comparator, not the connected checkpoint. Both current and historical adverse results are preserved. [Complete model/data/tool credits and unresolved license terms](../../docs/CREDITS.md).

- **Barakah application, identity, synthetic fixture and authored evaluation set:** this repository. Actual React/FastAPI UI was captured; its logo, colors and fonts were reused without redesign. No stock footage, testimonial, live market data or third-party financial records were used.
- **Historical evaluated model:** [LiquidAI/LFM3-1.7B](https://huggingface.co/LiquidAI/LFM3-1.7B), recorded revision `1da06bec6a819da10b54c67e5c90972b46d81871`; LFM Open License v1.0 as recorded in `benchmark/reports/MODEL_CARD.md`. Model weights were not redistributed. This model is **not connected to the filmed app**.
- **Benchmark dataset:** `benchmark/datasets/benchmark_questions.json`, dataset card, manifest and [source-evidence ledger](../../benchmark/datasets/SOURCE_EVIDENCE.md). 100 authored English questions; 40 arithmetic checks and 60 conceptual references pending expert review. External reference institutions include Islamic Relief Canada / Islamic Relief UK, National Zakat Foundation, Bank of England, Securities Commission Malaysia, and SEC Investor.gov. Their exact URLs, fetched passages, dates, hashes and limitations are in that ledger; source-checking is not endorsement or independent expert validation. Existing benchmark documentation also credits AI-assisted source research; preserve those credits in the submission.
- **Rules-based comparator:** the repository's deterministic calculator candidate, not a trained/fine-tuned model. No competitor or market-performance claim.

## Narration and sound

- **Narration:** [hexgrad/Kokoro-82M v1.0](https://huggingface.co/hexgrad/Kokoro-82M), Apache-2.0-licensed model weights according to the official model card. Uses supplied stock voice `af_heart`; no custom cloning or imitation of a named real person. Original narration text was authored for this production.
- **ONNX conversion/runtime:** [thewh1teagle/kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), v0.6.1, MIT. Model and stock voice downloads: [v1.0 release assets](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0). [Runtime license](https://github.com/thewh1teagle/kokoro-onnx/blob/main/LICENSE). The official model card's training-data acknowledgements include [Koniwa](https://github.com/koniwa/koniwa) (CC BY 3.0) and [SIWIS](https://datashare.ed.ac.uk/handle/10283/2353) (CC BY 4.0); preserved here as upstream attribution, not a claim these datasets were directly used by Barakah.
- **Music and transition tones:** original procedural sine/harmonic composition in `scripts/produce-audio.py`. No samples or commercial recording, no licensed track or sound-effect pack. Generated specifically for this film and available with its editable source.
- **Audio QA only:** [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper), MIT; [OpenAI Whisper](https://github.com/openai/whisper), MIT, tiny.en converted model. Local-only transcription; no film or audio was uploaded. This QA model does not power Barakah. ASR is imperfect and not treated as ground truth.

## Production software and fonts

- [Remotion](https://www.remotion.dev/), 4.0.543, including Media, Transitions, Captions and its bundled Chromium renderer. See [Remotion licensing](https://www.remotion.dev/license): this is an individual/small-team hackathon production; larger commercial reuse must check licensing. No claim of an organizer endorsement.
- [Basic Captions element](https://www.remotion.dev/elements/captions/basic-captions/): supplied source preserved in `src/basic-captions.element.tsx`; wrapper CSS uses Barakah colors.
- [Vercel agent-browser](https://github.com/vercel-labs/agent-browser) for real browser interaction and capture, Chromium, and [FFmpeg](https://ffmpeg.org/) for encoding/QA.
- [DM Sans](https://fonts.google.com/specimen/DM+Sans) and [Manrope](https://fonts.google.com/specimen/Manrope), SIL Open Font License. Original bundled font/license files copied under `assets/fonts/`. Georgia is the system editorial face already used by the product.
- React, TypeScript, Python, NumPy, SoundFile, ONNX Runtime and Pillow. JavaScript versions are pinned by `package-lock.json`; the local production Python environment is recorded in `reports/production-python-freeze.txt`.
- **AI production assistance:** OpenAI `gpt-6-astra` via the Pi coding-agent harness (`openai-codex` provider), including bounded research/audit/review subagents; OpenAI-backed web search for TTS licensing discovery. Used for repository inspection, official-rule research, script/source authoring, motion design, automation and QA. No generated AI product answer was inserted into the footage. Credit these tools in the submission form/write-up as required; using AI to make the video does not satisfy the event's core-product AI requirement.

## Competition sources

Official Veritas AI International High School Hackathon 2026 sources and linked Finance brief are listed with quotations in `REQUIREMENTS.md`. This project is not entered in Liquid AI's separate hackathons. All source/license checks were performed on 15 November 2026; licenses may change, so check before separate commercial reuse.
