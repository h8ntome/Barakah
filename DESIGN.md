---
name: Barakah
description: Calm, trustworthy, respectful Islamic-finance frontend prototype.
colors:
  emerald-950: "#062D23"
  emerald-900: "#073B2C"
  emerald-700: "#08603E"
  emerald-600: "#0B7750"
  mint: "#DFF3E3"
  sage: "#B3DEC0"
  canvas: "#FCFBF7"
  surface: "#FFF"
  ink: "#10241D"
  secondary: "#5D7065"
  border: "#E4EAE2"
  positive: "#087547"
  focus: "#2B8A62"
  mint-button-border: "#D0E9D2"
  mint-button-hover: "#CDEBD2"
  tag-ink: "#3C684A"
  tag-bg: "#EAF2E6"
  nav-selected: "#E7F1E5"
  nav-hover: "#EAF3E7"
  overview-border: "#E3E9DF"
  field-border: "#CCD9C6"
  field-prefix: "#617C5A"
  segmented-bg: "#EDF0E8"
  segmented-hover: "#E0E8D9"
typography:
  display:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "clamp(43px, 4.4vw, 68px)"
    fontWeight: 400
    lineHeight: 1.09
    letterSpacing: "-0.035em"
  brand:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "43px"
    fontWeight: 700
    letterSpacing: "-1px"
  headline:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "27px"
    fontWeight: 400
    letterSpacing: "-0.035em"
  title:
    fontFamily: "'DM Sans', sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.03em"
  body:
    fontFamily: "'DM Sans', sans-serif"
  label:
    fontFamily: "'DM Sans', sans-serif"
    fontSize: "11px"
    fontWeight: 500
  button:
    fontFamily: "'DM Sans', sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.4
  financial:
    fontFamily: "'Manrope', sans-serif"
    fontSize: "32px"
    fontWeight: 800
    lineHeight: 1.6
    letterSpacing: "-0.035em"
  financial-large:
    fontFamily: "'Manrope', sans-serif"
    fontSize: "37px"
    fontWeight: 800
    lineHeight: 1.4
    letterSpacing: "-0.035em"
rounded:
  sm: "12px"
  default: "16px"
  lg: "24px"
  field: "10px"
  tag: "5px"
  segment-track: "26px"
  segment-button: "22px"
spacing:
  space-1: "4px"
  space-2: "8px"
  space-3: "12px"
  space-4: "16px"
  space-5: "20px"
  space-6: "24px"
  space-8: "32px"
components:
  button-primary:
    backgroundColor: "{colors.emerald-700}"
    textColor: "{colors.surface}"
    typography: "{typography.button}"
    rounded: "{rounded.sm}"
    padding: "12px 15px"
    width: "100%"
  button-primary-hover:
    backgroundColor: "{colors.emerald-900}"
  button-mint:
    backgroundColor: "{colors.mint}"
    textColor: "{colors.emerald-700}"
    rounded: "{rounded.lg}"
    padding: "10px 22px"
  button-mint-hover:
    backgroundColor: "{colors.mint-button-hover}"
  money-input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    width: "143px"
  bottom-tabs:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.secondary}"
    typography: "{typography.label}"
  bottom-tab-selected:
    backgroundColor: "{colors.nav-selected}"
    textColor: "{colors.emerald-700}"
    rounded: "{rounded.sm}"
  demo-tag:
    backgroundColor: "{colors.tag-bg}"
    textColor: "{colors.tag-ink}"
    rounded: "{rounded.tag}"
    padding: "4px 6px"
  overview-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.default}"
    padding: "16px 16px 14px"
  segmented-control:
    backgroundColor: "{colors.segmented-bg}"
    rounded: "{rounded.segment-track}"
    padding: "4px"
  segmented-selected:
    backgroundColor: "{colors.emerald-700}"
    textColor: "{colors.surface}"
    rounded: "{rounded.segment-button}"
---

# Design System: Barakah

## Overview

**Creative North Star: "Calm, trustworthy, respectful Islamic finance"**

Barakah pairs a deep emerald editorial setting with a mint-and-offwhite financial interface. Serif brand and editorial moments provide warmth; compact sans-serif controls and emphatic financial numerals provide clarity. Thin borders, rounded surfaces and diffused shadows keep the interface quiet rather than ornamental.

The desktop is a showcase for one interactive phone, with an editorial panel on the left. On small screens the same app becomes edge-to-edge, retaining its five bottom destinations. This is strictly a frontend-only educational prototype: sample financial information, illustrative portfolios, local guide replies and demo giving intentions must remain visibly distinguishable from real services.

**Key Characteristics:**
- Deep emerald hierarchy with mint support and an offwhite canvas.
- DM Sans interface, Manrope financial totals, system-serif brand and editorial text.
- Rounded, thin-bordered surfaces with restrained, diffused elevation.
- One interactive app, persistent bottom navigation, responsive device framing.
- Visible demo context, keyboard focus and reduced-motion support.

Extraction authority: `src/styles.css` and `src/components/ui.jsx`; field and mint-button usage checked in `src/screens/Zakat.jsx`, with product limitations confirmed in `README.md` and `src/services/index.js`. YAML values are normative extracted defaults, not a redesign. The companion `.impeccable/design.json` contains only extensions and previews. Independent screenshot review was reported as SHIP; this extraction does not claim a new visual review.

## Colors

The palette is emerald-led, with warm neutral surfaces and pale green supporting tones. Frontmatter names preserve source custom-property names where available; descriptive state names identify repeatedly used literal values.

### Primary
- **Emerald 950:** desktop ground and deepest anchor.
- **Emerald 900:** dark brand surfaces and primary-button hover.
- **Emerald 700:** primary actions, selected segmented controls, active filter pills and active navigation text.
- **Emerald 600:** icon accents and input caret.
- **Mint / Sage:** soft supporting fills; sage also appears in text selection and desktop keyboard focus. These support the primary family, not a separate secondary brand palette.

### Neutral
- **Canvas / Surface:** offwhite app ground and white cards/fields respectively.
- **Ink / Secondary:** primary text and quieter explanatory text.
- **Border:** thin dividers and container outlines; the overview and money field retain their observed slightly different border colors.
- **Tag, navigation and segmented state colors:** pale fills belonging to those controls, not interchangeable new brand accents.

No synthetic tonal ramps are canonized: the source has named emerald shades and contextual pale fills, not an eight-step same-hue scale. Unobserved interpolation is intentionally omitted from the sidecar.

### Semantic and contextual accents
- **Positive:** illustrative growth labels; it is not evidence of guaranteed returns.
- **Focus:** visible keyboard and field-container outlines.
- Peach, blue, sage-tinted icon badges, cause illustrations and warm insight surfaces remain contextual accents. They are not a generalized secondary/tertiary palette. The unused root coral variable is not promoted into this normative palette.

## Typography

**Display / Brand Font:** Georgia, then Times New Roman, then generic serif. This is an operating-system fallback stack, not a bundled or custom brand face; exact serif appearance varies by platform.

**Body Font:** DM Sans, then sans-serif. A local variable font supplies weights (400–700).

**Financial Font:** Manrope, then sans-serif. A local variable font supplies weights (400–800). Prominent totals use weight (800), tight tracking and tabular numerals; ordinary row values can stay in DM Sans with tabular numerals.

### Hierarchy
- **Display:** fluid desktop editorial heading, with size, weight and line-height in the `display` token. Compact desktop heights use `clamp(42px, 4vw, 59px)` instead.
- **Brand:** bold serif wordmark; the outlined arch mark is an authored SVG, not a font glyph.
- **Headline:** serif home and giving headings. Other editorial moments are contextual (education 25px, modal 26px, empty/success 24px); do not force all into one size.
- **Title:** centered screen header. Section headings use (16px, 700, -0.02em).
- **Body:** the source establishes a family, not one global body-size/line-height pair. App prose is commonly (11–13px), with contextual line-height (1.6–1.85); desktop supporting copy uses (15px, 1.8).
- **Label:** bottom-tab label default; selected tabs become weight (700). Demo tags use (10px, 600, 1.3), with smaller overview/chat instances.
- **Financial / Financial large:** dashboard and estimate totals respectively. Portfolio totals are (34px); at narrow widths dashboard totals become (29px), portfolio totals (31px).

**The Type Roles Rule.** Use DM Sans for controls, Manrope for prominent financial totals, and the existing system-serif stack for brand/editorial moments; do not describe Georgia as a shipped custom face.

No mathematical type-scale ratio or global prose measure is established. Fonts are bundled under `public/fonts/`; standalone previews use the same family stacks but require the host's font faces to display the bundled faces.

## Layout

- Desktop uses two grid columns (`minmax(420px, 1fr)` and `minmax(470px, .9fr)`). The left editorial panel has maximum width (770px); the right region centers a single phone. Desktop navigation controls the same app state as bottom tabs, not a second app.
- The framed phone is (410px) wide, with height `min(880px, calc(100dvh - 80px))` and minimum height (650px). Its inset screen owns scrolling; bottom tabs remain outside the scrolling content.
- At viewport widths (980px and below), the left panel is hidden and the framed phone is centered alone. At (600px and below), remove frame, side button, caption, borders, frame padding and frame shadow; use full width and (100dvh) height with square outer screen corners.
- At (365px and below), reduce page gutters, figures, charts and selected labels: standard inner-screen padding changes from (19px) to (14px), home padding from (17px) to (13px). The page minimum width is (320px).
- A separate compact-desktop query applies at widths (981px and above) and heights (850px and below): tighten editorial padding, heading size, navigation and gaps. This is a height adaptation, not a new mobile breakpoint.
- Spacing tokens preserve the source's (4px) base steps; component layouts also have contextual measurements, so this is not an exclusive spacing grid. Standard inner screens end with (25px) bottom padding. The home overview overlaps the hero by (26px).
- Bottom navigation uses five equal columns, minimum height (70px), and (48px) minimum-height tab targets. Preserve top and bottom safe-area insets on mobile. Icon buttons are (44px) targets; primary buttons have minimum height (48px), mint and segmented buttons (44px) and (42px) respectively.

**The Single App Rule.** Keep one interactive phone on desktop and the same edge-to-edge app at small widths; do not turn the editorial panel into another financial dashboard.

## Elevation & Depth

Depth combines pale tonal fills, thin (1px) borders and deliberately soft shadows. The overview card is lightly lifted; the device and native modal have separate structural elevation. Flat lists use dividers instead of adding a shadow to every row.

### Shadow Vocabulary
- **Overview card:** `0 7px 18px #092B1410` — subtle lift over the hero/canvas.
- **Desktop device:** `0 30px 65px #001A1399, 0 0 0 4px #203F30` — device grounding plus outer ring; removed at edge-to-edge widths.
- **Modal:** `0 24px 70px #001A1444` — native dialog elevation. Backdrop is `#03271FC7`; no blur is implemented.

Buttons and inputs transition background and border color over (0.16s, ease). The loading spinner rotates over (1s, linear, infinite). Reduced-motion preference disables animations and transitions and restores automatic scrolling across elements and pseudo-elements. There is no observed screen-slide, hover-lift or spring-motion system.

## Shapes

Use gently rounded cards and controls: the reusable radius tokens are small (12px), default (16px) and large (24px). This aligns with the requested roughly 12–18px card character; the implemented common card radius is specifically (16px), not a newly imposed 18px token.

Keep component-specific exceptions: icon badges (14px), money fields (10px), tags (5px), segmented tracks/buttons (26px/22px), search (25px), composer (27px), modal (23px), and circular icon/avatar treatments. Desktop device/frame corners are (50px/40px), becoming square edge-to-edge. Chat bubbles use (16px) corners with one speaker-side lower corner reduced to (4px). Do not flatten these distinctions into a single radius.

## Components

### Buttons
Confident fills without heavy effects. Primary buttons fill the available width, use emerald 700 with white text, small corners, padding (12px 15px), gap (8px) and minimum height (48px). Default top margin is (19px). Hover changes to emerald 900 only when enabled. Mint buttons are inline pill-like secondary actions, with padding (10px 22px), minimum height (44px), mint fill and a thin mint-toned border; hover uses the extracted mint-hover fill.

Text actions are emerald, with minimum height (44px), padding (5px 7px) and underlined hover. Circular icon controls have transparent resting backgrounds and a pale-green hover. There is no separate generic outline-button API. Keyboard focus on buttons is a (3px) solid focus outline offset (3px), except desktop navigation uses sage. Disabled buttons have opacity (.55) and a not-allowed cursor; do not invent a new disabled palette or active transform.

### Chips
Demo tags are compact, noninteractive labels on pale green, with extracted tag colors, padding (4px 6px) and corners (5px). Retain labels such as “Sample data,” “USD prototype” and “Local demo” where the source uses them; they are disclosure, not decorative confidence badges.

Giving category filters are interactive pills: minimum height (44px), corners (24px), padding (9px 15px), thin border and muted text at rest. Active filters use emerald 700/white and weight (600); unselected hover is `#E8F1E2`. Selected state is also conveyed by `aria-pressed`, not color alone.

### Cards / Containers
The financial overview uses white, a thin overview-specific border, default corners, padding (16px 16px 14px) and the light overview shadow. Its heading and sample tag share a row; the total and illustrative sparkline share the next region. Large numbers may wrap rather than overflow. Breakdowns use white bordered containers, muted row dividers and a mint total row. Cause/asset/holding lists favor flat rows and fine separators; do not add overview shadows to every row.

### Inputs / Fields
Money fields use a white container with thin field border, corners (10px), minimum height (45px), default width (143px) and a currency prefix. The inner input has padding (11px 7px), size (13px), tabular numerals, ink text and emerald caret. Focus is on the wrapper: (2px) focus outline offset (2px). Narrow asset fields use width (123px); custom giving amounts use full width.

Search and chat inputs are pill-shaped white containers. Search focus uses the same (2px) outline and offset; composer focus offset is (1px). Placeholders use secondary text at full opacity. Inline errors are pale warm surfaces with a thin warm border, small corners and readable dark warm text; validation is not represented by an invented red field-border state.

### Navigation
Bottom tabs persist in a five-column canvas-colored bar with a thin top border. Labels use the extracted label role; icons are (21px) strokes (1.8), increasing to (2.2) when selected. Selected tabs have a pale-green rounded fill, emerald text and bold labels; hover uses the navigation-hover fill. Preserve `aria-current="page"` and the order Home, Invest, Zakat, AI Chat, Give. Desktop navigation uses the same destinations with expanded titles, (20px) line icons, transparent resting rows and a dark-green selected treatment.

### Segmented control
A two-option, pale neutral-green rounded track with padding (4px), gap (4px) and emerald-filled selection. Options have minimum height (42px), type (13px), and weight (500). Unselected hover uses the extracted segmented-hover fill. Keep group labeling and `aria-pressed`; the preview shows visual states, not a framework-powered selector.

### Dialogs and status
Native modal dialogs use the canvas, thin green border, padding (22px), maximum width (440px) constrained to viewport minus (30px), and maximum height `calc(100dvh - 36px)`. Preserve focus containment, focus return, Escape/backdrop dismissal and busy-state dismissal protection. Keep loading, empty and retry states legible; reduced motion must not hide status text. Notice boxes explain educational limitations without presenting an endorsement seal.

## Do's and Don'ts

### Do:
- **Do** keep the extracted emerald hierarchy, mint supporting fills and offwhite canvas.
- **Do** preserve the distinct UI, financial-number and system-serif type roles.
- **Do** keep persistent bottom tabs, scrollable content, visible keyboard focus and mobile safe areas.
- **Do** honor reduced motion and retain legible loading/retry/empty states.
- **Do** retain sample-data, educational-estimate and demo-intention disclosures alongside financial content.

### Don't:
- **Don't** add a second interactive desktop phone or stretch the financial app into the left editorial panel.
- **Don't** invent a new accent palette, universal 18px radius, tonal ramp or shadow-heavy card system.
- **Don't** call the fallback serif a bundled brand font or assume a universal body-size scale.
- **Don't** imply connected backends, real payments, live model replies, live market feeds, certified securities or guaranteed returns.
- **Don't** add hover lifts, spring transitions, blurred backdrops or new active/error-field styles absent from the implementation.
