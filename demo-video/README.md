# Barakah — the demo film

## Reviewed personal-provider update

The selected v2 candidate is `output/user-connections-review/barakah-demo-user-connections-yuv420p-v2.mp4`, SHA-256 `3107c2e1673b2a0a75dd49896061cbd77b318ef48113ae5820494b9735a54fc9`: 115.008 seconds, 16,043,571 bytes. [Measured QC](reports/USER_CONNECTIONS_V2_VALIDATION.json), [playback](reports/USER_CONNECTIONS_V2_playback-check.json), [narration](reports/USER_CONNECTIONS_NARRATION.md), and [preservation manifest](reports/USER_CONNECTIONS_preservation.json). Independently decoded and visually reviewed; subjective listening was not performed. The older master below is preserved until separately promoted into the final package.

Current source uses isolated candidate audio/captions. After restoring the real capture assets and local TTS runtime described below, run `python scripts/produce-audio.py --candidate` using that TTS environment, then `npm test`, `npm run lint`, and `node scripts/render-user-connections.mjs`. The candidate renderer refuses overwrites and never promotes a master. Generated WAVs, SRT and MP4 remain local/ignored; a fresh clone must regenerate them before media tests/rendering. The verified review used an explicitly approved installed Chrome executable through `REMOTION_BROWSER_EXECUTABLE` after bundled Chromium failed; this override is not needed for ordinary environments.

The historical master/release evidence below is not a claim that personal-provider inference succeeded.

**Finished master:** [`output/barakah-demo-final.mp4`](output/barakah-demo-final.mp4)

**Quick preview:** [`output/barakah-demo-preview.mp4`](output/barakah-demo-preview.mp4)

**Thumbnail:** [`output/thumbnail.png`](output/thumbnail.png)

115.000 seconds of video (115.008-second MP4 container), 1920×1080, 30 fps, H.264/AAC stereo. See `reports/VALIDATION.json` for exact size and hash. Captions are burned in and supplied separately in `output/barakah-demo-captions.srt`.

> **Final-release status:** private local AI is connected to pinned `h8notme/barakah1` (revision `912a5697cf9d85adf065ee512f509cfa236459d4`). The genuine response gets $825 right but recommends high-yield savings despite no-interest instructions; the follow-up fails to account for a $200 parental transfer (available surplus should be $625). Advice is unverified. Public AI at `https://barakah-gamma.vercel.app` remains unavailable. Current numeric results: original **36/40**, candidate **32/40**; on the same 15 zakat tasks, rules **15/15**, candidate **11/15**. Sixty conceptual answers remain unreviewed; the neutral benchmark prompt differs from the app prompt. No superiority, improved safety or competition eligibility is claimed. See [current release evidence and QA](reports/FINAL_RELEASE.md).

## What is included

- Editable Remotion timeline: `src/BarakahDemo.tsx`, eight scene components in `src/scenes.tsx`, common visual elements in `src/components.tsx`.
- Real screen recordings and screenshots: `assets/recordings/`, `assets/screenshots/`.
- Original synthesized score, licensed stock TTS narration, final mix and phrase-aligned captions: `assets/audio/`.
- Timestamped script: [`reports/NARRATION.md`](reports/NARRATION.md), authored timing in `scripts/narration.json`.
- Official requirements, full repository evidence, runtime test results, claim mapping, credits and QA: `reports/`.
- Isolated demo database/process logs/model caches: `.runtime/` (private/local/ignored).

## Reproduce an export with the saved assets

Requires Node 20.19+ (or supported newer), Python 3, and FFmpeg/ffprobe on PATH. Saved recordings and WAVs exist in the release workspace but are intentionally Git-ignored; a fresh clone must recreate them using the capture/audio steps below before rendering. The submitted MP4 is self-contained.

```sh
cd demo-video
npm ci
npm test
npm run lint
npm run render
```

The render script renders a candidate, validates every frame/audio limits, then replaces the final file; the previous valid master is preserved. It makes the smaller preview and thumbnail. Remotion downloads and uses its own bundled browser. **No alternative recording browser is used for rendering.**

On this Mac the bundled Chromium 158 has a reproducible native `requestAnimationFrame` failure. `src/render-clock.ts` provides a render-only, single-fire timer fallback, with tests. Frame time remains exclusively Remotion-controlled; this is not a wall-clock animation. The app itself is unaffected. Both the initial and corrected full renders succeeded. Remove this shim only after a bundled-browser callback probe and full render pass on a fixed version.

## Preview and edit

```sh
npm run dev -- --port=3095
```

Open `http://localhost:3095/BarakahDemo`. Scene timings and each clip are named authored JSX nodes; headings and primary copy expose Remotion interactive elements. Generated captions come from PCM-aligned JSON and are edited in `scripts/narration.json`, not the Studio caption editor. Computed counts/allocation widths and reused frame layouts are source-controlled rather than individually editable Studio keyframes. The root is exactly 3,450 frames, including transition overlap.

## Recreate the real app capture

From repository root, with the project's existing backend venv and frontend dependencies installed:

```sh
python3 demo-video/scripts/prepare-demo.py start
python3 demo-video/scripts/capture-demo.py
python3 demo-video/scripts/verify-evidence.py
```

The original capture script recreates the financial scenes and an unavailable-AI scene. For the current live scene, separately configure the real service using `../docs/local-ai.md`, run `tests/e2e/ai_live.py` with `BARAKAH_AI_RECORDING` pointing to `assets/recordings/ai-live.mp4`, and retain its response JSON/screenshot. Do not substitute canned responses. New capture results require truthful claim/QA review, not blind reuse of this release's observed failure text.

This uses `127.0.0.1:8095`, a dedicated `demo-video/.runtime/demo.sqlite`, and an independent frontend build. It does not overwrite the default app database, frontend build, production records, or running teammate servers. Capture uses installed `agent-browser` with isolated browser sessions. The local `scripts/bin/ffmpeg` adapter uses `/opt/homebrew/bin/ffmpeg`; adjust that one path for another OS. Source browser viewport is 440×850 at 2× density; desktop is 1440×900.

The existing **Try Demo** feature creates a real authenticated owner. Settings renames the fictional user to Amina Rahman. No password, token or cookie is recorded or committed. Its 24-hour expiry means future captures should create a fresh account. Other November 2026 captures are preserved. The final-release AI scene uses the separately supplied genuine `ai-live.mp4`, `ai-live.png` and `reports/ai-live-evidence.json`; do not rerun the historical capture script to replace that scene. The legacy capture script demonstrates the older unavailable-AI build, not the release inference path. For the other scenes, the date-filter fixture is intentionally pinned to the filmed month. For a different month, update the two capture month inputs together and re-verify the footage and labels.

Stop only the owned services with:

```sh
python3 demo-video/scripts/prepare-demo.py stop
```

## Recreate narration and score

The licensed model and voice bundle are existing ignored caches, never Git artifacts. In this isolated copy the venv is shared read-only; the TTS cache directory is local, with read-only links to existing model/voice/line assets so generated lines and `fitted.wav` stay in the copy. Do not recreate the shared venv or install dependencies here.

```sh
cd demo-video
.runtime/tts-venv/bin/python scripts/produce-audio.py
```

This uses Kokoro v1.0's supplied `af_heart` voice, not a custom voice clone. Music and transition tones are original procedural synthesis. Phrase timings follow generated waveform durations; restrained pitch-preserving tempo adjustment fits the reserved slots. Review regenerated speech and re-render if text or voice changes.

## Validation

```sh
cd demo-video
npm run validate
python3 scripts/playback-check.py
# Optional independent local ASR QA:
# Existing local QA environment already includes faster-whisper.
.runtime/tts-venv/bin/python scripts/audio-review.py
```

The final-release MP4 is fully decoded and scanned for black frames, silence and clipping. Current sampled export-frame, playback and ASR results are recorded in `reports/FINAL_RELEASE.md`; earlier independent review reports are explicitly historical and are not approval of this new export. ASR is supplemental, not subjective listening or proof of pronunciation.

No upload, publication, commit or push was performed. Generated MP4s, raw recordings, waveforms, model caches and private runtime state are ignored by Git but preserved locally. Keep the saved assets when transferring this editable production folder.
