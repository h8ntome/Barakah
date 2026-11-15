# Barakah

<!-- impeccable:product-schema 1 -->

## Platform
web

## Stack
React 18, Vite, lucide-react and standard CSS, integrated with FastAPI, SQLAlchemy and Alembic. PostgreSQL preferred; SQLite local fallback.

## Users
Young adults and households learning faith-aligned personal finance, including beginners unfamiliar with zakat, nisab, and investment screening.

## Product Purpose
Islamic Finance for a Blessed Tomorrow. Help people track their finances, estimate and record Zakat, monitor manually entered investments, record Sadaqah and learn with an educational finance guide.

## Capabilities and Constraints
Five destinations: Home, Invest, Zakat, AI Chat, Give. The full-stack implementation supersedes the original frontend-only assignment. Authenticated services persist records; financial arithmetic is server-authoritative and per-currency. No actual payment processing, bank/broker linking, live market feed or certification. AI is unavailable by default/publicly; explicit local opt-in connects a pinned checkpoint after saved consent. No fabricated replies or automatic financial-record sharing. Model suggestions are not Sharia-screened and have observed advice failures. Local integration is separate from model training and neutral-prompt benchmarking. Preserve the existing visual design and benchmark work.

## Brand Commitments
Barakah spelling; emerald, mint and off-white palette; refined serif wordmark; mosque arch/crescent logo; approachable, respectful, financially credible voice. The user explicitly pins the visual world and composition: an emerald desktop editorial panel and one interactive phone, becoming edge-to-edge on mobile.

## Evidence on Hand
`barakah-ui/reference/barakah-concept.png` supplied concept image; existing React UI in `barakah-ui/src/`. No verified securities, charities, religious rulings, or personal financial data.

## Product Principles
- Make interactions persist real user-owned records, never pretend they moved money.
- Teach without implying a fatwa, certification or personalized advice.
- Keep transport/provider boundaries separate from page layouts; label every manual/mock source.
- Keep financial totals coherent when assets change.

## Accessibility & Inclusion
320px to desktop; readable text, visible focus, labeled fields, keyboard navigation and dialogs, reduced-motion support, loading/error/retry/empty states. Avoid a single universal scholarly method or regional threshold.

## Open Decisions
Live market/provider credentials, public model hosting, scholarly methodology approval, advertiser/charity vetting and production infrastructure remain operator decisions. See docs/RELEASE_AUDIT.md and docs/local-ai.md for current verified scope and limitations.
