# Final-release film — 15 November 2026

## Delivered artifact

- Master: `/tmp/barakah-release-video/demo-video/output/barakah-demo-final.mp4`
- SHA256: `861898670c31a6cc4bf5656e7d6677ec1c3dab7759d137f3cbdceb68a9994ade`
- Video: **115.000 seconds**, 3,450 frames, 1920×1080, 30 fps, H.264/yuv420p. MP4 container: **115.008 seconds**. Size: **13,933,017 bytes**.
- Audio: AAC stereo, 48 kHz; **−16.09 LUFS**, **−1.45 dBTP**.
- Preview and SRT regenerated. Thumbnail re-rendered, byte-identical to supplied thumbnail.
- Prior good master automatically preserved at `output/barakah-demo-previous.mp4`, verified against input SHA256 `d6be8f2bd891aca08205d2a06b4007c8fe80a045976381b6f243ba7b207be61d`.

## Current story / bounded claims

Other real captures, scene timings, visual identity and opening narration remain intact. The sole opening typography fix replaces existing irregular whitespace on source line 12 with regular spaces.

At 65–77 seconds, the original 177-frame (5.9-second) live recording plays at normal speed, followed by the supplied screenshot reading hold. The scene states browser → backend → pinned model, private local/not hosted, `h8notme/barakah1` revision `912a5697cf9d85adf065ee512f509cfa236459d4`. Public `barakah-gamma.vercel.app` AI remains unavailable. Identity metadata is service-attested, not an independent weight audit. Supplied footage/evidence were used, not recaptured or mocked.

At 77–91 seconds, a readable crop of the actual screenshot shows correct $825 surplus and the contradictory high-yield savings recommendation despite no-interest instructions. The exact follow-up excerpt dismissing the $200 parental transfer is alongside the correction: available monthly surplus should be $625. This is an observed adverse result, not an improvement claim. The historical arithmetic example is omitted from this film to prioritize the current failure; its reports/assets remain preserved.

At 91–107 seconds, original numeric **36/40** vs candidate **32/40**, plus simple rules **15/15** vs candidate **11/15** on the same 15-task zakat subset. `release-comparisons.json` records the two source paths, run IDs, raw metrics and source SHA256; tests verify their hashes where the supplied benchmark symlink exists. Sixty conceptual answers are unreviewed. The neutral benchmark prompt differs from the application prompt. No superiority or verified advice/safety gain is claimed.

Closing: **Local AI connected · Advice unverified · Public AI unavailable**. See `CLAIMS_AND_EVIDENCE.md` for claim mapping and `NARRATION.md` for generated timings.

## Validation actually performed

- `npm test`: timeline/caption bounds, narration-caption text/start equality, live identity and raw adverse-response checks, corrected $625 arithmetic, all four comparison scores and common candidate run, source hashes, required current caveats/no stale claims, existing scheduler tests.
- `npm run lint`: TypeScript passed. `npx eslint src`: passed, including original irregular-whitespace fix. Node scripts also passed with their `console` global explicitly supplied: `npx eslint scripts/check-source.mjs scripts/render-video.mjs --global console`.
- `.runtime/tts-venv/bin/python scripts/produce-audio.py`: all 19 PCM-aligned phrases regenerated/fitted inside their reserved slots; 115-second mix and JSON/SRT captions regenerated.
- `npm run render` using the unchanged production render script, existing bundled Remotion browser and explicit 1,800-second shell deadline: passed candidate validation before master replacement, then final validation, preview and thumbnail.
- Candidate and final completely decoded: all **3,450 frames**; no decode errors, no near-total black frames, no silence below −60 dB longer than one second, loudness/peak limits passed. Full-frame validation is machine decoding, not a claim to have visually inspected every frame.
- Five preflight full-resolution stills inspected at 68, 72, 80, 98 and 111 seconds. Export contact sheet inspected across the entire timeline, including 70.8/70.9-second live-video/screenshot boundary. Full-resolution final MP4 frames at 80, 100 and 114 seconds inspected: current response, failure, both denominators, review/prompt caveats and closing legible with no overlapping substantive copy. Saved in `release-export-frames/`, contact sheet in `release-export-contact-sheet.jpg`.
- `python3 scripts/playback-check.py`: uninterrupted real-time local browser playback to `ended=true` at 115.008, no media error, zero reported dropped frames at all samples. Used a release-specific session; closed it. This is playback observation, **not subjective listening**.
- `HF_HUB_OFFLINE=1 .runtime/tts-venv/bin/python scripts/audio-review.py`: existing Whisper tiny.en model copied into the isolated runtime; local offline ASR recovered all changed financial/comparison numbers and status statements. It rendered “no-interest instructions” as “no interest in instructions” and names phonetically (“Barreca”, “Zachat”); ASR is imperfect QA, not ground truth. No listening or pronunciation-panel approval is claimed.
- Hash checks confirm **every supplied screenshot and recording is byte-identical**, original score is byte-identical, and prior good master was preserved. No recapture, parent source edit, package install, shared dependency edit, benchmark rewrite, commit, staging, push, upload or public-site change.

## Historical evidence and limits

Earlier unavailable-AI reports have explicit historical banners. Reports overwritten by regeneration were first copied to `historical-pre-release/`; old frame folders/contact sheets and capture/test logs remain historical. `REQUIREMENTS.md` is prior research, not freshly checked. Historical independent review is not approval of this replacement master. Current independent reviewer acceptance remains for the parent gate.

The initial broad ESLint invocation included Node scripts without Node globals and reported only `console` no-undef; the proper scoped checks above pass. A contact-sheet helper invoked system Python lacking Pillow; rerunning under the existing TTS venv succeeded. No render/tool installation failed and no blocker remains. No dependency audit remediation or package write-up was attempted; those belong to the parent.

This isolated directory is not a Git worktree and has no staging index. `release-changed-files.json` lists exact changed/new non-runtime paths and hashes, plus local runtime changes. Model advice remains flawed/unverified, public AI unavailable, and subjective audio review outstanding. No competition eligibility determination is made.
