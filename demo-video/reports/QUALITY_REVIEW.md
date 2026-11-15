> **Historical pre-release report — not current release status or approval.** This document describes the earlier unavailable-AI build/export. Local AI is now connected, advice remains unverified, and public AI remains unavailable. See [FINAL_RELEASE.md](FINAL_RELEASE.md) and [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md) for the current film. Original findings below are preserved, not reasserted.

# Final quality review

## Status

**Delivered and validated:** `output/barakah-demo-final.mp4`, SHA256 `d6be8f2bd891aca08205d2a06b4007c8fe80a045976381b6f243ba7b207be61d`.

This passes the video-production/media checks. It does **not** establish hackathon eligibility: live AI and a model advantage over a simple baseline remain missing, visibly disclosed.

## Complete review and iteration

1. Rendered a complete first 115-second master, decoded all 3,450 frames and measured its audio. Kept it while reviewing.
2. Inspected the whole timeline via 5-second contact-sheet samples and full-resolution frames. An independent fresh-context reviewer inspected ten additional full-resolution frames, captions and repository evidence.
3. Found the historical model excerpt's first equation had white text on a white card at 01:17–01:31. Changed the card foreground to dark green, rendered a complete replacement and validated that new file before replacing the master.
4. Extracted the corrected **01:20** frame from the actual final MP4 (`final-frames/080-fixed-excerpt.png`) and visually verified both the equation and the wrong/correct results are readable. This is verification of the export, not merely the source edit.
5. Independently inspected the rendered thumbnail. Corrected its inherited headline color and re-rendered it; the final 1920×1080 thumbnail is readable and uses genuine app screenshots.
6. Played the final MP4 **uninterrupted at real-time speed in a local browser**, with audio enabled, from zero to `ended=true` at 115.008 seconds. Captured states every ten seconds and selected playback screenshots. Every sample had `readyState=4`, no media error and **zero reported dropped frames**. This is a playback/decoding observation, not a claim of subjective listening. See `playback-check.json`.

## Visual/content checks

- All eight primary scene intervals retained, with one honest archival cutaway inside the AI interval.
- Genuine authenticated app and synthetic fixture remain central. UI details use unaltered recorded screenshots, with intentional magnification, not fabricated controls.
- Headline, value labels, chart numbers, disclaimers and caption samples readable at 1080p; secondary phone UI is intentionally supported by large value callouts/detail crops.
- Original app logo, emerald/mint/ivory palette and type retained. No personal identity, school, password, access token, cookie, debug console or browser error page appears in the film.
- Expected assistant unavailable state is deliberate and necessary, not disguised as successful inference. The preferred Hajj prompt is real. Historical benchmark is explicitly labeled, and its exact output is not changed.
- No live market, guaranteed return, certified halal, expert-validation, team fine-tuning or production-readiness claim.
- Small single-run comparison: original model 12/15, rules calculator 15/15. The calculator's advantage is stated, not reframed as AI improvement.
- Forty arithmetic / sixty pending conceptual reviews, all five category counts and $375 arithmetic confirmed independently.
- Smooth 12-frame dissolves, no near-total black frames or missing media detected in final scan. Intentional readable holds are not concealed inference wait time or claimed frame-rate performance.

## Audio/caption checks

- Final AAC stereo at 48 kHz; −16.08 LUFS integrated; −1.49 dBTP true peak. No clipping and no silence below −60 dB longer than one second.
- Nineteen authored phrases match caption text and start times; all end inside reserved slots. Music/tones are original synthesis; no unlicensed track or voice clone.
- Local Whisper tiny.en transcription independently recovered all substantive spoken sentences and financial/comparison numbers with matching approximate intervals. It spelled Islamic names phonetically (e.g. “Barreca”, “Zachat”, “hadged”) and hallucinated “Thank you” over the closing score; **these ASR strings are not authoritative transcripts**. The generated narration has exactly zero voice samples after 112 seconds (last utterance ends 111.135), proving no extra “thank you” was inserted into the spoken track. `audio-asr-review.json` is retained transparently as imperfect supplemental QA.
- No human listening/pronunciation panel was available; native pronunciation and subjective music taste are not independently certified. No video/audio was uploaded for analysis.

## Final media

| Artifact | Result |
|---|---|
| Master | 1920×1080, 30 fps, H.264/yuv420p, 3,450 decoded frames, 13,861,571 bytes |
| Duration | Video 115.000 s; container 115.008 s (AAC padding), under 120 s |
| Preview | 1280×720, 30 fps, H.264/AAC stereo, 115.008 s, 4,680,796 bytes |
| Thumbnail | PNG, 1920×1080, inspected after contrast correction |
| Captions | Burned in; separate 19-cue SRT and JSON/Markdown transcript |
| Decode/black/silence checks | Passed over complete master |
| Browser playback | Completed uninterrupted, no media errors, zero reported dropped frames |

## Scope and residuals

No human scholarly/financial validation, live inference, remote upload test or public deployment verification. Current working-tree changes outside `demo-video/` were left untouched. No commit/push/publication. The original first master is retained locally at `.runtime/first-render.mp4`; final media and production assets remain in this folder.
