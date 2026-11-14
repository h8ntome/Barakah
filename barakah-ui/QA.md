# Local validation

Validated on 2026-11-14 with Node 26.12.1, npm 11.20.0, Vite 7.3.8 and headless Chromium via agent-browser.

## Automated checks

- Dependency installation completed; final dependency tree audited with **0 vulnerabilities**.
- `npm test`: **16/16 passing** (money arithmetic/rounding, liability clamping, validation, isolated JSON-ready fixtures, async behavior, saves/dashboard consistency, fault-safe retry, cause filters, demo intentions, deterministic advisor responses, allocations).
- `npm run build`: **passed** in the supplied `barakah-ui/` directory and the local validation snapshot. Final app bundle approximately 187 kB JS / 61 kB gzip, 28 kB CSS / 7 kB gzip, plus local fonts.
- Mechanical UI detector: no findings (`[]`).
- Independent read-only reviewer: **SHIP — frontend prototype**, no material findings after inspecting source, contract and 16 screenshots. The named Impeccable reviewer was unavailable; the installed general reviewer performed this review. Final focus corrections were subsequently verified in Chromium and recaptured.
- No existing lint script was supplied; no lint-pass claim is made.

## Browser interaction evidence

Production preview was served from an exact source snapshot outside Documents because iCloud repeatedly offloaded active checkout files. The same final source built successfully in the supplied directory. Local dependencies were placed outside the synced folder for validation; dependencies and build output are not committed.

- Rendered and visually inspected 1440×1000, 1280×800, 768×1024, 390×844 and 320×640. Document width matched the viewport at 320px and 1280px; no horizontal page overflow observed. Inner app content scrolls separately above the persistent bottom navigation.
- Home shortcuts, bottom tabs and desktop navigation reach their destinations.
- Cash changed from 12,000 to 13,000: preview and Zakat show **643.75 USD**, Home shows **25,750 USD**. Negative input is rejected; Escape cancels without saving.
- Dialog Tab/Shift+Tab explicitly cycle from last to first control; Escape closes and restores focus to Edit assets. Dialogs scroll within 320×640.
- Investment Explore renders three educational criteria. Portfolio allocations total 100%, holdings are labeled fictional.
- Search with nonexistent text renders an empty result and Clear filters. Education filter returns two causes; only one category is pressed.
- Custom gift **12.34 USD** produces the matching thank-you with “Demo only — no money moved.” No payment or receipt is created.
- All starter-response mappings are covered by tests; the savings starter was browser-checked against its monthly-plan reply. Enter sends custom text. Messages remain when switching away and back.
- Injected dashboard/cause read errors recover with Try again. Injected save retains cash draft; donation retains cause/amount; advisor retry produces one user bubble and one assistant bubble.
- Empty portfolio and empty causes render appropriate guidance. Slow-mode capture shows pending loading and then success.
- Final browser error buffer: **empty**. Performance resource origins: **no cross-origin requests** (fonts/services are local).

## Limits

Headless Chromium checks are not a full screen-reader, real-device, Safari/Firefox, or regulatory/religious audit. The live backend, payment, authentication, AI, charity and compliance integrations are deliberately absent. Current data and schemas are mock/proposed, not verified or agreed backend facts.

See README for reproducible steps and mock query controls. Browser screenshots are local review artifacts, excluded from Git.
