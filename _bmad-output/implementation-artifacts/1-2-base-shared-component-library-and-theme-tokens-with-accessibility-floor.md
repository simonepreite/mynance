---
baseline_commit: d1fbf34
---

# Story 1.2: Base shared component library and theme tokens with accessibility floor (UX-DR1, UX-DR2, UX-DR12)

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the builder,
I want the shared "Morbido" components and theme tokens implemented with the accessibility floor baked in,
So that all later screens compose from one consistent, accessible, light/dark-ready component set rather than ad-hoc styling.

## Acceptance Criteria

- **AC1 — Token set.** Given the theme layer from Story 1.1, when the app loads in light or dark, then the documented token set is available as CSS custom properties — including `color.accent`/`color.accent-ink`, `color.positive`/`color.positive-ink`, `color.negative`, `color.honesty`/`color.honesty-bg`, `color.ink`/`color.ink-soft`, `color.surface`/`color.surface-2`, `color.bg`, `color.bar-track`, `color.focus`, `radius.card`, and the `type.display`/`type.body`/`font.sans` typography tokens — and switching theme re-resolves every component's appearance without a reload.
- **AC2 — Component library.** Given the shared component namespace, when the library is built, then the base behavioral components exist and are reusable: `card`, `balance-block`, `bottom-nav`, `honesty-banner`, `list-row`, `chip`, and a generic button/input set — each styled solely from theme tokens (no inlined colors, radii, or fonts).
- **AC3 — Focus ring.** Given any interactive element, when it receives keyboard focus, then it shows a visible 2px focus ring using the dedicated `color.focus` token (never the soft `color.accent`), and focus traversal follows reading order.
- **AC4 — Contrast & tap targets.** Given the accessibility floor, when text is rendered in either theme, then normal body text meets WCAG AA (≥ 4.5:1) using the text-safe `-ink` variants and `color.ink-soft` for secondary text, and every tap target (chip, nav slot, list row, button) is ≥ 44px.
- **AC5 — Honesty color rule.** Given the honesty color rule, when a component renders a warning or surfaced truth, then it uses warm amber `color.honesty` on `color.honesty-bg`, never alarm-red; `color.negative` is reserved only for negative signed figures; and sign is never conveyed by color alone — a `+`/`−` plus the figure always accompanies it.
- **AC6 — Reduce Motion.** Given a user with Reduce Motion enabled, when an animated component would appear, then the animation is skipped and the end state is shown immediately.

## Tasks / Subtasks

- [ ] **Task 1 — Typography & token completeness (AC1)**
  - [ ] Add the typography tokens to `frontend/src/theme/tokens.css` as CSS custom properties: `--font-sans`, `--type-display`, `--type-h1`, `--type-h2`, `--type-body`, `--type-caption` (font shorthands referencing `--font-sans`), plus `--tracking-display`/`--tracking-h1` and `--weight-*`. Apply `font-family: var(--font-sans)` at the root.
  - [ ] Add typography utility classes (`.type-display`, `.type-h1`, `.type-h2`, `.type-body`, `.type-caption`, `.type-eyebrow`) in `index.css` so components carry type solely from tokens.
  - [ ] Confirm all AC1 color tokens already resolve from 1.1 (`--m-*` + shadcn slots + `@theme` Tailwind utilities) and that switching theme re-resolves them with no reload.
- [ ] **Task 2 — Accessibility floor primitives (AC3, AC4, AC6)**
  - [ ] A reusable focus-ring (2px, `--m-focus` via `ring-focus`, `focus-visible` only — never `--m-accent`).
  - [ ] A `prefers-reduced-motion: reduce` base rule that neutralizes animations/transitions so the end state shows immediately.
  - [ ] Tap-target floor: every interactive element ≥ 44×44px (`min-h-11 min-w-11`).
- [ ] **Task 3 — Shared component library (AC2, AC3, AC4, AC5)** under `frontend/src/components/morbido/`:
  - [ ] `card`, `balance-block` (hero Netto, `type.display`, explicit `+`/`−` sign, `-ink` colors), `bottom-nav` (≥44px slots, accent-ink active indicator), `honesty-banner` (amber on amber-bg, never red), `list-row` (≥44px), `chip` (pill, selected = accent-soft, ≥44px), generic `button` + `input`. Token-only styling; barrel `index.ts`.
- [ ] **Task 4 — Gallery harness + e2e (all ACs)**
  - [ ] `frontend/morbido-gallery.html` (multi-page dev entry, pre-paint theme script) + `frontend/src/dev/morbido-gallery.tsx` rendering every component with `data-testid`s and a theme toggle. Out of the router (no `routeTree.gen.ts` change), dev-only.
  - [ ] `frontend/tests/morbido.smoke.spec.ts` (theme project) asserting: token custom properties incl. typography; theme re-resolves; 2px `color.focus` ring on keyboard focus; tap targets ≥44px; honesty amber colors (not red); `+`/`−` sign present; reduce-motion end state.
  - [ ] Broaden `playwright.config.ts` `theme` project `testMatch` (and `chromium` `testIgnore`) to `*.smoke.spec.ts`; update the CI step name.
- [ ] **Task 5 — Verify** biome clean; CI green (tsc+build, theme e2e on Chromium).

## Dev Notes

### Token values — verbatim from DESIGN.md (source of truth)
Colors already in `theme/tokens.css` from 1.1 (light/dark `--m-*` + shadcn slots + `@theme` utilities: `bg-surface`, `text-ink`, `text-ink-soft`, `text-honesty`, `bg-honesty-bg`, `text-accent-ink`, `text-positive-ink`, `text-negative`, `bg-accent-soft`, `bg-bar-track`, `rounded-card`/`-panel`/`-pill`, `ring-focus`). [Source: DESIGN.md frontmatter]

Typography (to add): `font.sans = -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`; `type.display ~46px/800/-0.03em` (hero Netto); `type.h1 ~30px/800/-0.02em`; `type.h2 ~15–17px/800`; `type.body ~15px/500`; `type.caption ~12px/600`. Radius: `card 34px`, `panel 24px`, `control 18px`, `pill 999px`.

### Architecture compliance (binding)
- `theme/` owns all visual tokens; shared components under `components/`; `features/` never recompute derived money. [Source: architecture.md#Architectural-Boundaries, #Complete-Project-Directory-Structure]
- **Anti-patterns:** inlined colors/radii/fonts in components; reusing `color.accent` for the focus ring; alarm-red for honesty; conveying sign by color alone.

### A11y floor (UX-DR12)
- 2px focus ring with `color.focus` (`#527A6D` light / `#9CC4B5` dark), `focus-visible` only.
- AA contrast via `-ink` variants for figures/icons and `color.ink-soft` for secondary text.
- ≥44px tap targets. Non-color signifiers: explicit `+`/`−` with every figure; honesty in warm amber, never red; `color.negative` only for negative signed figures.
- Reduce Motion → skip animation, show end state immediately.

### Testing
- Playwright e2e in the `theme` (no-auth) project, served by `bun run dev`. Component-level a11y assertions run against the dev-only `morbido-gallery.html` to avoid touching the auth router / generated route tree. [Source: architecture.md#Testing]

## Dev Agent Record

### Completion Notes List

### Change Log

| Date | Change |
|---|---|
| 2026-06-16 | Story drafted from epic 1.2 + DESIGN.md + architecture; status in-progress. |

### File List
