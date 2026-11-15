> **Historical pre-release report — not current release status or approval.** This document describes the earlier unavailable-AI build/export. Local AI is now connected, advice remains unverified, and public AI remains unavailable. See [FINAL_RELEASE.md](FINAL_RELEASE.md) and [CLAIMS_AND_EVIDENCE.md](CLAIMS_AND_EVIDENCE.md) for the current film. Original findings below are preserved, not reasserted.

# First-render independent QA

**Gate: hold for the already-queued contrast fix; no additional must-fix visible, caption-text, or honesty problems found in the sampled frames.**

## Must fix
- **01:17–01:31 — archived calculation card:** the first equation is almost white on white, making the evidence for “right formula, wrong arithmetic” unreadable. Confirmed directly at **01:20** in [frame-80.png](frame-80.png). This is the known queued fix, not a new finding. Current `src/scenes.tsx` already specifies dark card text, but the inspected first MP4 still contains the defect. Verify the replacement render, not just source.

## Checks completed
- `ffprobe -v error -show_format -show_streams output/barakah-demo-first.mp4`: **1920×1080, 30 fps, 3,450 frames, H.264/yuv420p; AAC stereo 48 kHz; video 115.000 s, container 115.008 s; 13,849,918 bytes**. No subtitle stream; captions are burned in, with separate SRT supplied.
- Full decode via `ffmpeg -hide_banner -v error -i output/barakah-demo-first.mp4 -f null -` completed without errors.
- Read the supplied contact sheet and actual full-resolution extracted frames at **00:24, 00:39, 00:59, 01:13, 01:20, 01:34, 01:43, 01:48, 01:50, 01:54**. Frames saved only alongside this external report. Sampled captions are readable, not clipped, and do not obscure substantive caveats. Closing captions are correct at 01:48/01:50 and absent at 01:54.
- Read scene/composition/caption source, narration JSON, caption JSON, SRT, claims matrix, and repository-evidence report. Read-only assertions confirmed all **19** narration/caption texts and start times match, with caption ends inside narration slots.
- Independently checked original benchmark metadata, raw `ZAKAT_007`, comparison JSON, and dataset: exact archived wrong answer **246.61** exists; Decimal calculation gives **246.91**; matched comparison **12/15 versus 15/15**; dataset **100**, category counts **25/25/20/20/10**, review split **40 arithmetic / 60 pending expert**. The film presents the narrow result and limitations honestly.
- **01:05–01:17 / 01:47–01:55:** unavailable AI and pending integration are transparent; no invented response or implied functioning live model found. Keep these disclosures.
- No repository edits, staging, uploads, publishing, or service/database calls performed. `git diff --cached --name-only` was empty. Only this report and extracted PNG evidence were written outside the repository.

## Checks not performed
- No real-time audiovisual playback/listening: pronunciation, music balance, clicks, subjective pacing, and actual spoken-word/caption synchronization remain unchecked.
- No exhaustive frame-by-frame transition review, small-screen playback test, live app retest, independent expert religious/financial validation, or replacement-render verification.

**Next step:** render the queued contrast correction, inspect the archived equation in the resulting MP4, then perform one uninterrupted audiovisual playback before final approval.
