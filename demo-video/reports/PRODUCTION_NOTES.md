> **Historical pre-release report — not current release status or approval.** This document describes the earlier unavailable-AI build/export. Local AI is now connected, advice remains unverified, and public AI remains unavailable. See [FINAL_RELEASE.md](FINAL_RELEASE.md) and [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md) for the current film. Original findings below are preserved, not reasserted.

# Production notes

## Editorial decision

The intended AI hero scene could not truthfully be shot: this checkout deliberately removed all model-serving paths, accepts only `AI_MODE=unavailable`, and responds 503 to a real assistant request. Connecting a new model would be a separately approved product/safety implementation, not a small recording fix. No fake answer was substituted. The final film shows the genuine attempt, then an explicitly archival LFM3-1.7B response and failure. The closing says **AI integration pending**, not “AI-powered” as an existing capability.

The proposed $18,000/$450 zakat and $320 giving figures were not used. The existing authenticated demo fixture supplies coherent $15,000/$375 and $125 figures. All financial values are fictional USD records; the portfolio uses fictional manual quotes and has no verified screening. No account values were altered merely to improve a claim.

## Final 115-second timeline

| Time | Editorial purpose | Actual source |
|---|---|---|
| 00:00–00:08 | Immediate money-and-values hook | Original animated typography, existing logo/palette |
| 00:08–00:18 | Product introduction | Captured authenticated desktop app |
| 00:18–00:34 | Dashboard proof | Real month changes, spending, Transactions navigation; magnified genuine screenshots |
| 00:34–00:46 | Zakat with assumptions | Actual server calculation and saved immutable snapshot |
| 00:46–00:51 | Giving | Recorded sadaqah history, $125; no transfer |
| 00:51–01:05 | Investment awareness | Actual manual holdings/allocations and Learn tab; unverified screening visible |
| 01:05–01:17 | Honest AI status | Actual Hajj/savings prompt and unavailable response |
| 01:17–01:31 | Technical failure evidence | Exact archival ZAKAT_007 excerpt, corrected Decimal arithmetic alongside |
| 01:31–01:47 | Evaluation | Narrow 12/15 vs 15/15 result; 100-question coverage and 60 pending expert reviews |
| 01:47–01:55 | Impact and close | Brand, value proposition, pending-AI status, no-financial-advice disclaimer |

The app's emerald/mint/ivory palette, serif editorial type, local fonts and arch/crescent mark were retained. Subtle arch outlines, soft frames, a gentle desktop push, precise 12-frame dissolves, count-ups and allocation highlights complement rather than replace the real screen recordings. Cursor overlays are captured during actual interactions. Magnified UI details are labeled recorded details, not reimplemented app controls. Reading holds may retain a captured final frame; no generated successful state or advice is added.

## Audio

Kokoro v1.0 `af_heart` supplied stock voice, original scripted English narration, phrase-level PCM timing. Original procedural harmonic bed and restrained transition tones, no stock samples. Narration is mixed clearly above the low-level stereo bed, then normalized. Final measured loudness: −16.08 LUFS integrated; true peak −1.49 dBTP. Nineteen caption phrases match the authored script; JSON, SRT and timestamped Markdown are included. Captions are shown in a dedicated lower safe area, not over substantive application details.

## Capture and rendering

- Isolated application: `127.0.0.1:8095`, dedicated SQLite and build output under `.runtime/`; migrations only against that new DB.
- Browser: unique agent-browser sessions; 440×850 at 2× density, desktop 1440×900. Actual Try Demo auth, synthetic name saved through Settings, reload-persistence checks.
- Build: Remotion 4.0.543, 1920×1080, 30 fps, 3,450 frames, H.264 yuv420p + AAC stereo 48 kHz.
- Container is 115.008 seconds due to AAC sample padding; the video stream is exactly 115.000 seconds.
- Remotion's bundled Chromium 158 had a reproduced rAF scheduling failure independent of the composition. `render-clock.ts` adds a rendering-only one-shot timer fallback; its fallback, native, cancellation and non-render paths are tested. Contrary to the diagnosis report's suggested browser override, **the alternative browser was not used**. Bundled-browser rendering completed successfully twice.
- The first full render was preserved. Its white-on-white archival equation was identified by direct and independent review, corrected, and re-rendered. The final MP4 was checked again; see `QUALITY_REVIEW.md`.
- The thumbnail received a separate root-text-color correction after inspection. It does not alter the master film.

## Safety and scope

No app source, benchmark dataset/result, model weight, default database, teammate branch or production record was changed. No training or expensive evaluation rerun. No Git commit/push and no upload/publication. Only dependencies required for video/capture/audio/QA were installed; generated media and caches are ignored by Git. Late concurrent changes appeared outside `demo-video/` (deployment-related root/backend files); they were left untouched. Audit/test claims apply to the captured build and recorded commit, not an assertion that later unrelated edits were retested.

## Remaining limits

No live AI; no demonstrated advantage over a simple rule; conceptual and safety evidence is not expert-verified. No real payments, bank sync, brokerage, live quotes or certification. No user-impact study. No human pronunciation/listening panel: local ASR and automated signal/playback checks supplement visual review, not subjective native-listener approval. All core-product competition eligibility concerns remain explicit in `SUBMISSION_GUIDANCE.md`.
