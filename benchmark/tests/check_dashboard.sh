#!/usr/bin/env bash
# Browser integration against actual saved results, not synthetic benchmark outputs.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
SESSION=barakah-benchmark-check-$$
OUT="$ROOT/visuals/20261115/verification"
mkdir -p "$OUT"
trap 'agent-browser --session "$SESSION" close >/dev/null 2>&1' EXIT
ab() { agent-browser --session "$SESSION" "$@"; }
ab open "file://$ROOT/visuals/20261115/html/index.html"
ab set viewport 1440 1000
ab select '#outcome' regressed
ab eval 'if(document.querySelector("#visible-count").textContent!=="4 questions shown")throw Error("Outcome filter"); "4 regressions shown"'
ab select '#category' budgeting
ab eval 'if(document.querySelector("#visible-count").textContent!=="3 questions shown")throw Error("Category filter"); "3 budgeting regressions"'
ab select '#difficulty' difficult
ab eval 'if(document.querySelector("#visible-count").textContent!=="1 questions shown")throw Error("Difficulty filter"); "1 difficult budgeting regression"'
ab fill '#search' 'NO_MATCH_643210'
ab eval 'if(document.querySelector("#empty").hidden)throw Error("Empty state"); "Empty state visible"'
ab click '#reset'
ab select '#category' investing
ab eval 'if(document.querySelector("#visible-count").textContent!=="25 questions shown"||!document.querySelector("#filtered-a").textContent.includes("No numerical score"))throw Error("Conceptual score"); "25 conceptual questions, no numeric score"'
ab select '#chart' 07_resources
ab eval 'if(!document.querySelector("#chart-image").src.endsWith("07_resources.svg"))throw Error("Chart selector"); "Chart selector works"'
ab click '#reset'
ab select '#chart' 01_numerical_accuracy
ab fill '#search' BUDGET_006
ab click 'details[data-question]:not([hidden]) summary'
ab eval 'const d=document.querySelector("details[open]");if(!d||d.querySelectorAll(".answer").length!==2||!d.textContent.includes("1310.00"))throw Error("Response comparison"); "Both real responses expand"'
ab set viewport 390 844
ab eval 'document.querySelector("details[open]").scrollIntoView({block:"start"})'
ab screenshot "$OUT/mobile-response.png"
ab eval 'document.querySelector("#reset").scrollIntoView({block:"center"})'
ab click '#reset'
ab eval 'document.querySelectorAll("details[open]").forEach(e=>e.open=false);window.scrollTo(0,0)'
ab screenshot "$OUT/mobile.png"
ab eval 'if(document.documentElement.scrollWidth>innerWidth)throw Error("Mobile overflow"); "390px layout has no horizontal overflow"'
ab set viewport 1440 1000
ab eval 'window.scrollTo(0,0)'
ab screenshot "$OUT/desktop.png"
ab eval 'if(document.documentElement.scrollWidth>innerWidth||document.querySelectorAll("[data-question]").length!==100||[...document.images].some(i=>!i.complete||!i.naturalWidth))throw Error("Desktop integrity"); "1440px layout, 100 question pairs, all images loaded"'
ab errors
ab open "file://$ROOT/visuals/20261115/html/review.html"
ab eval 'if(document.querySelectorAll("details").length!==60)throw Error("Blinded review coverage"); "60 blinded question pairs"'
echo 'PASS: dashboard filters, missing-score state, chart switching, response expansion, desktop/mobile layout and blinded review coverage'
