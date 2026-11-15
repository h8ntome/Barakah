# Remotion render timeout diagnosis

## Concrete cause and fastest workaround

The installed **Chrome Headless Shell 158.0.8127.2 does not execute `requestAnimationFrame` callbacks on this Mac**, even on a plain HTML page with no React, Remotion bundle, fonts, or media. Timers execute and `document.visibilityState` is `visible`. This explains the exact Remotion root-handshake timeout.

The already-installed **Chrome Headless Shell 156.0.8078.4** works with the same Remotion launcher and its default Chromium flags: **42 animation callbacks in 700ms**, versus **0** for 158. No download, dependency downgrade, or source modification is needed.

Use this browser override immediately:

```bash
npx remotion still src/index.ts BarakahDemo output/review-dashboard.png \
  --frame=780 \
  --browser-executable="$HOME/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell"
```

Then use the same override for production:

```bash
npx remotion render src/index.ts BarakahDemo output/barakah-demo.mp4 \
  --browser-executable="$HOME/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell"
```

This is a **validated browser-level workaround**, not a claim of a completed end-to-end video render. No render was run during diagnosis.

## Evidence linking the browser failure to the log

- `src/index.ts` synchronously calls `registerRoot(RemotionRoot)`; `src/Root.tsx` registers `BarakahDemo` with 3450 frames, 30fps, 1920×1080.
- `.runtime/still.log` and `.runtime/still-explicit.log` both show initial **“Loading root component” cleared after 0ms**, followed by a timeout for the distinct **“Waiting for root component to load”** handle.
- Installed `node_modules/@remotion/studio/dist/esm/renderEntry.mjs:289–298` sets evaluation mode, creates that second handle, obtains the registered root and calls `renderContent(Root)`, then clears the handle **only inside `requestAnimationFrame`**.
- `node_modules/remotion/dist/cjs/register-root.js` invokes `waitForRoot` callbacks synchronously when the root already exists. Therefore initial successful registration does not guarantee that the later animation-frame continuation will run.
- `node_modules/@remotion/renderer/dist/select-composition.js` switches to evaluation mode and waits for readiness before calculating composition metadata. This happens before rendering frame 780; increasing the timeout or changing frame/content does not solve this isolated failure.
- `node_modules/@remotion/renderer/dist/browser/get-chrome-download-url.js:41` pins the installed default to `158.0.8127.2`; the browser itself reports that version.
- Process inspection showed agent-browser uses the working cached `chromium_headless_shell-1248` executable, explaining why Studio works there.

## Bounded isolation results

Each probe opens a fresh browser using `@remotion/renderer.openBrowser`, navigates to a `data:text/html` page, schedules a recursive animation callback, waits 500–700ms using `setTimeout`, reads the count and visibility, then closes the browser in `finally`.

| Browser/options | Result |
|---|---|
| Default bundled 158, plain HTML, 700ms | 0 frames, visible |
| 158, `gl: 'swangle'` | 0 frames |
| 158, `--disable-gpu` | 0 frames |
| 158, `--disable-frame-rate-limit` | 0 frames |
| 158, `--run-all-compositor-stages-before-draw` | 0 frames |
| 158, background throttling/occlusion flags plus disabling CalculateNativeWinOcclusion | 0 frames |
| 158, `--enable-begin-frame-control` (without explicit begin-frame driving) | 0 frames |
| 158, ANGLE + SwiftShader + unsafe SwiftShader | 0 frames |
| 158, `--headless=new` | 0 frames |
| 158, disable PaintHolding | 0 frames |
| Cached 156, otherwise default Remotion options, 700ms | **42 frames, visible** |

Bringing the page to the front did not help the 158 flag probes. Remotion already supplies `--disable-background-timer-throttling`, `--disable-backgrounding-occluded-windows`, and `--disable-renderer-backgrounding` by default. No successful minimal GL/background flag workaround was found; overriding the browser executable is the demonstrated fix.

### Reproduce the decisive A/B without rendering or modifying project files

```bash
node <<'NODE'
const {openBrowser} = require('@remotion/renderer');
(async () => {
  for (const options of [
    {},
    {browserExecutable: process.env.HOME + '/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'},
  ]) {
    const browser = await openBrowser('chrome', options);
    try {
      const page = await browser.newPage({
        context: () => null, logLevel: 'error', indent: false,
        pageIndex: 0, onBrowserLog: null, onLog: () => {},
      });
      await page.goto({url: 'data:text/html,<body style="background:red">RAF probe</body>', timeout: 3000});
      console.log(options, await page.evaluate(async () => {
        let frames = 0;
        const tick = () => { frames++; requestAnimationFrame(tick); };
        requestAnimationFrame(tick);
        await new Promise(resolve => setTimeout(resolve, 700));
        return {frames, visibility: document.visibilityState, ua: navigator.userAgent};
      }));
    } finally {
      await browser.close({silent: true});
    }
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
NODE
```

## Scope and remaining uncertainty

No project files or npm packages were edited; only this requested findings artifact was written. No tests were added and no production/still render was attempted. Browser probes create and clean up ordinary temporary browser profiles. `git diff --cached --name-only` produced no output: no staged files.

The precise upstream Chromium 158 regression or machine-specific trigger has not been established; the browser-version A/B isolates the operational cause and supplies an immediately available workaround. React 19.3.1, the two bundlers, and project content are unnecessary to reproduce this failure. A successful still with the executable override is the next production gate; unrelated downstream asset/media problems remain untested.
