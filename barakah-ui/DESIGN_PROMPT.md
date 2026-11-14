# Barakah — Master UI/UX Design & Frontend Development Prompt

## Product mission

Design and build **Barakah**, a premium, approachable, mobile-first Islamic personal-finance app with the tagline **“Islamic Finance for a Blessed Tomorrow.”** The experience helps Muslims understand their finances, estimate zakat, manage a Sharia-conscious investment portfolio, plan voluntary sadaqah, and ask questions in an AI-powered finance guide. Barakah must balance **financial credibility, religious respect, ease of use, and warmth**. The interface should look like a polished, launch-ready fintech application, without copying a conventional banking app or becoming overly ornate.

The accompanying file `reference/barakah-concept.png` is the inspiration. It shows a wide dark-emerald promotional composition with five iPhone mockups: Home, Zakat Calculator, Sharia-Compliant Portfolio, AI Financial Advisor, and Sadaqah & Giving. Recreate its visual language and main structure while improving tiny text, consistency, readability, accessibility, and small-screen behavior. The application itself should be interactive, not simply a picture of the mockup.

## Audience and design principles

Target young adults and households interested in faith-aligned money management, including beginners who may be unfamiliar with nisab, asset screening, or investment terms. The experience should feel welcoming to people who are learning. Use plain language with clear explanatory microcopy, discreet educational footnotes, and easy-to-understand financial numbers. Avoid presenting unverified companies as categorically Sharia-compliant or generic educational information as a fatwa, personalized financial advice, or validated compliance certification.

Core brand characteristics: **trustworthy, calm, intelligent, respectful, hopeful, modern**. Avoid gambling-like trading visuals, sensational return claims, overly busy Islamic motifs, and fear-based messaging about zakat. Elegant rather than flashy.

## Brand identity

- Product name: **Barakah**. Spelling and capitalization must remain consistent everywhere; never use an earlier working name.
- Primary tagline: **Islamic Finance for a Blessed Tomorrow**.
- Logo direction: an elegant mosque-arch outline incorporating a crescent and small star; optionally render a geometric crescent inside a shield/arch mark. The lockup should use a refined serif wordmark reading “Barakah.” Do not use Quranic calligraphy merely as decoration.
- Deep emerald base: `#062D23`, `#073B2C`, and `#08603E`.
- Medium emerald for active controls: `#0B7750` or `#13885A`.
- Mint and sage highlights: `#DFF3E3`, `#B3DEC0`, `#9CCFAE`.
- Off-white app canvas: `#FCFBF7`; surfaces: `#FFFFFF`.
- Body/heading ink: `#10241D`; secondary text: `#6F7E74`.
- Positive trend: `#10965A`; negative trend: muted coral `#B45B55`.
- Charitable categories may use restrained water blue, peach, sage, and sandstone.
- Main interface typography: **DM Sans** or a similarly legible modern sans serif. Use **Manrope** for large financial numbers and a restrained **Georgia-like serif** for the Barakah brand and occasional editorial headings.
- Rounded cards: 12–18px. Buttons: 12–30px depending on placement. Subtle diffused shadows, thin gray/green borders, clear vertical rhythm, and generous white space.
- Icon style: simple 1.8–2.3px rounded line icons in a consistent family such as Lucide.

## Layout, responsiveness and navigation

The app should have five primary destinations: **Home**, **Invest**, **Zakat**, **AI Chat**, **Give**. On mobile, provide a persistent bottom tab bar with an icon and a concise label for each destination; the active state should use emerald green. Secondary screen headers show a back arrow on the left and a centered title. The content scrolls independently from the bottom navigation; top status-bar styling is optional in a production mobile app but is useful in a web-based device preview.

For desktop widths, show a branded emerald left-side panel, an oversized editorial product statement, a compact navigation list and a single realistic phone preview to the right. The phone can display any of the five interactive screens. On a narrow mobile viewport, remove all ornamental desktop framing and present the app edge-to-edge. Ensure accessible touch targets, readable body text, strong contrast, visible keyboard focus, and sensible empty states. Use CSS-grid/flexbox and responsive breakpoints. The mockup's five phones are for a showcase graphic, not a requirement to display five tiny phone panels in the actual working app.

## Screen 1 — Home / financial dashboard

**Purpose:** give an immediately useful summary and guide users to the main pillars of Barakah.

1. Top hero is deep emerald with a subtle silhouette of mosque domes and minarets, crescent, gentle gradients, and a welcoming greeting such as “Assalamu Alaikum” followed by “Welcome to Barakah.” Add a small circular profile monogram or avatar to the right. The background imagery should be restrained enough not to interfere with the text.
2. A large white rounded summary card overlaps the bottom of the hero. Label: “Your Financial Overview.” Show a sample **Total Net Worth of $24,750** (editable indirectly through the Zakat asset editor), a compact emerald rising sparkline, and an illustrative green percentage such as “+4.2% (30d sample).” The performance percentage and sparkline are demo display elements and do not derive from live markets.
3. Four equal quick-action tiles with pastel icon containers: **Zakat** (stacked coins), **Sadaqah** (heart), **Invest** (bars), and **AI Advisor** (sparkles). They must navigate to the actual corresponding destinations.
4. A “Your priorities” section with an estimated zakat item and an “Update your assets” item. Both must be interactive. The estimate should derive from local entered values, not remain a hard-coded disconnected number.
5. A soft warm-gray “Today's Insight” card with a sun/sparkle icon and one concise faith-sensitive financial habit tip. Avoid invented religious quotations.
6. Use appropriate data/sample tags so a tester does not confuse the prototype with their actual balances.

## Screen 2 — Zakat calculator

**Purpose:** explain and estimate a charitable obligation without falsely claiming religious authority.

1. Minimal white/off-white screen, back arrow, centered “Zakat Calculator” title.
2. Large pale-mint circle containing a stacked-coins icon.
3. Label “Your Estimated Zakat,” prominently display the calculated amount in bold large typography, then a short explanation stating it is calculated from entered assets and liabilities.
4. Centered mint “Edit assets” button with pencil icon. Opens a dialog/form allowing edits to **Cash & bank balances, Eligible investments, Gold & silver, Business assets, and Deductible liabilities**. Use nonnegative numeric inputs.
5. Breakdown card with rows for total assets, liabilities, illustrative nisab threshold, illustrative zakat rate, and a mint-highlighted “Estimated Zakat Due” total.
6. Asset list below with matching icons and values.
7. Prototype formula: `eligible_base = max(0, sum(entered_asset_values) - entered_liabilities)` and `illustrative_zakat = eligible_base × 0.025`. Show the computed amount in both Home and Zakat screens.
8. Display the illustrative nisab as a **nonlive example**, not as a universally current or region-independent threshold. Add a visible educational note saying real zakat eligibility depends on precious-metal rates, lunar holding period, asset categories, debt treatment, and scholarly methodology; consult a qualified scholar for a definitive ruling.
9. Future backend should provide locally relevant, dated commodity prices, nisab methods, currency selection, haul tracking, payment history, reminders, and auditability.

## Screen 3 — Sharia-conscious portfolio

**Purpose:** convey wealth growth and portfolio organization without falsely certifying securities.

1. Header: “Halal Investing” or “Sharia-Compliant Portfolio.” Segmented switch between **My portfolio** and **Explore**.
2. On My portfolio show sample value **$18,420**, green “+6.8% (30d sample)” and a clean emerald rising sparkline.
3. A pale mint/lilac trust banner with shield-check icon and text encouraging verification through a reputable and current Sharia screening methodology. Do not mark a nonverified portfolio “100% Sharia-compliant.”
4. Allocation heading and a donut chart. Use the illustrative category split: **Diversified 40%, Healthcare 20%, Consumer 18%, Energy 12%, Other 10%**. Each category has a color dot and percentage legend. Add a readable total amount in the center of the donut.
5. A few labeled, explicitly fictional holdings below the chart and a clear action to explore investing concepts. Do not pretend the fictional holdings are real tickers.
6. Explore shows three concise educational review cards: business activities, financial ratios, and ongoing monitoring. Mention the changing status of compliance, methodology differences, and the need for verification.
7. Future product functionality may support broker integrations, real holdings, vetted screening vendors, up-to-date financial statements, portfolio purification estimates, and risk disclosures. The initial frontend must not place real orders or suggest guaranteed returns.

## Screen 4 — AI financial advisor

**Purpose:** provide a calm, useful, conversational entry point for budgeting, saving, zakat education, and Sharia-conscious investing.

1. Header “AI Financial Advisor” and a subtle sparkle icon; add a small status label clarifying the current implementation is a **demo**.
2. Conversation layout: user prompts align right on soft mint bubbles; assistant replies align left inside warm-white/soft-gray cards. Assistant messages include a tiny circular emerald sparkle avatar. Maintain comfortable padding and readable line height.
3. Start with “Assalamu Alaikum!” and a short welcome mentioning the four topics: budgeting, zakat, sadaqah, and Sharia-conscious investing.
4. Show suggested starter questions when the conversation is empty: “How do I calculate zakat?”, “What makes a stock halal?”, and “Help me create a savings plan.” Clicking one should insert and answer that question.
5. Sticky lower message composer with placeholder “Ask about Islamic finance...” and a circular emerald send control. Support Enter/send form behavior and retain the conversation while the tab remains mounted; scrolling should follow new messages.
6. In this prototype, use clearly labeled deterministic local example responses. A future LLM backend could use a curated finance dialogue dataset and retrieval from vetted sources, with transparent limitations, sensitive-data handling, safety checks, source attribution, and scholarly review. Do not imply a generic financial dialogue dataset automatically makes the assistant an Islamic-finance expert.

## Screen 5 — Sadaqah & giving

**Purpose:** make giving approachable and trackable.

1. Back navigation, centered “Sadaqah & Giving” title.
2. Friendly green heart icon within a pastel mint circle, centered “Give Sadaqah” heading, and a short uplifting description.
3. Rounded search field with search icon and placeholder “Search causes...”. Filtering should update the visible cause cards.
4. Horizontal filter pills: **All**, **Education**, **Relief**, **Masjid**. Exactly one active selection, shown as a filled emerald pill.
5. Scrollable cause list. Each cause card contains an attractive rounded illustration/thumb, a title, funding figures, an emerald progress bar and a chevron. Initial sample causes: **Provide Clean Water** ($3,420/$5,000), **Support Orphans** ($7,800/$10,000), **Build a Masjid** ($12,500/$20,000), and **School Supplies** ($1,900/$4,000).
6. Clicking a cause opens an accessible donation dialog with description, preset amounts of $10/$25/$50/$100, a custom amount field, and a confirm action. Confirming displays an explicit **demo-only** thank-you; no payment occurs.
7. Charity names, funding status and beneficiaries are illustrative. A real product must vet charities, obtain consent, secure payment processing, transparently distinguish zakat-eligible donations from sadaqah, and issue receipts.

## Component architecture

Build reusable components for the **brand logo/lockup, screen header, bottom tabs, primary button, segmented control, quick action tile, financial overview card, sparkline, colored icon badge, information notice, asset row, portfolio legend, donation cause card, and modal**. Use a central design system with reusable radius, spacing, typography and color decisions. Keep sample data separate from live user data, and make it clear when values are illustrative. Ensure buttons and tabs are meaningful, not decorative. At minimum, navigation, editable assets, category filters, search, donation modal/confirmation, and chat demo responses must work.

## State and computation

- Keep `activeTab` in React state.
- Keep a structured `assets` object in React state; update it from a controlled form.
- Derive net worth and estimated zakat from that object on each render.
- Keep investment segments, donation categories, search query, chosen cause, amount, and simulated confirmation as controlled state.
- Keep local demo chat messages in state. For an actual AI provider, replace only the response generation function with a secured server API; **never put API keys in browser source**.
- Use formatters for currency and dates; clearly annotate the default USD currency as a prototype choice. Support PKR and other currencies in a future product through an explicit setting and trustworthy FX data.
- Respect reduced-motion preferences; keep transitions subtle.

## Copywriting and content quality

Favor supportive, neutral wording: “Estimated zakat,” “Explore investment criteria,” “Plan your giving,” “Sample portfolio,” “AI guide.” Avoid false confidence such as “Guaranteed halal,” “100% compliant” without verified screening, “Donate now” when no real donation takes place, or “AI scholar” unless it truly has qualified oversight. Use the words **zakat**, **sadaqah**, **nisab**, and **Sharia** accurately and consistently. The audience may be from many countries and interpretive traditions; avoid assuming a single universal threshold or jurisprudential position.

## Accessibility and UX acceptance criteria

- Responsive and usable at 320px phone widths through large desktop screens.
- Keyboard reachable navigation, buttons, form controls, and modals; visible focus states.
- Labels for icon-only buttons and search/chat fields.
- Clear text contrast and legible financial amounts; no color-only indication for gains/losses or selection.
- Empty state for a filtered search with zero results.
- Real-time recalculation after asset edits and coherent totals everywhere.
- Clear distinction between explanatory prototype features and verified/live data.
- No broken controls, no horizontal overflow on mobile, no content trapped beneath the bottom navigation.
- Run a production build successfully.

## Implementation specification for this handoff

Use **React 18 + Vite**, **lucide-react** for icons, standard CSS for styling, and local state only. The result must be a standalone project with `package.json`, `index.html`, `src/main.jsx`, `src/App.jsx`, `src/styles.css`, and a README with setup commands. Do not require secrets or external backend services. The project bundled with this prompt already implements this minimum functional frontend. The polished promotional illustration is provided separately as a reference rather than embedded behind interactive controls.

## Future production roadmap (not implemented)

Phase 1: user auth, multi-currency budgets, persistent user assets, account settings, locale-aware zakat setup, zakat year/calendar tracking.

Phase 2: verified current Sharia screening sources and documented methodology, portfolio data integrations, investment education, audited donation partners and payments.

Phase 3: LLM-backed advisor with secure API, dataset evaluation, grounded retrieval/citations, guardrails against unsuitable personalized advice, language localization, alerts and reporting.

**Final output expectation:** deliver an interface that looks recognizably like the reference Barakah concept but works as a real frontend demo with consistent navigation, realistic state management, attractive spacing and typography, and honest disclosure of limitations.
