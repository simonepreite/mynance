---
title: mynance — Visual Identity (DESIGN.md)
status: final
created: 2026-06-15
updated: 2026-06-15
# Tokens per Google Labs design.md spec — direction "Morbido" (source: mockups/direction-morbido.html)
colors:
  light:
    color.bg: '#F4F1EA'
    color.surface: '#FBFAF6'
    color.surface-2: '#EFEAE0'
    color.ink: '#3A3A38'
    color.ink-soft: '#6D6A63'
    color.accent: '#7FA99B'
    color.accent-ink: '#527A6D'
    color.accent-soft: '#DDE8E2'
    color.positive: '#6B9B7C'
    color.positive-ink: '#4D725A'
    color.negative: '#A05C43'
    color.honesty: '#8B6237'
    color.honesty-bg: '#F6E9D8'
    color.bar-track: '#EAE4D8'
    color.focus: '#527A6D'
  dark:
    color.bg: '#21201D'
    color.surface: '#2C2A27'
    color.surface-2: '#353230'
    color.ink: '#ECE7DD'
    color.ink-soft: '#A29D92'
    color.accent: '#9CC4B5'
    color.accent-ink: '#9CC4B5'
    color.accent-soft: '#38463F'
    color.positive: '#93C4A0'
    color.positive-ink: '#93C4A0'
    color.negative: '#D89479'
    color.honesty: '#E0B080'
    color.honesty-bg: '#423526'
    color.bar-track: '#3A3733'
    color.focus: '#9CC4B5'
typography:
  font.sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
  type.display: '46px / 800 / -0.03em (hero Netto number)'
  type.h1: '30px / 800 / -0.02em (screen title)'
  type.h2: '15-17px / 800 (card / section heading)'
  type.body: '15px / 500 (default text)'
  type.caption: '12px / 600 (labels, meta)'
  weight.regular: 500
  weight.semibold: 700
  weight.black: 800
rounded:
  radius.card: 34px
  radius.panel: 24px
  radius.control: 18px
  radius.pill: 999px
spacing:
  space.1: 4px
  space.2: 8px
  space.3: 12px
  space.4: 16px
  space.5: 20px
  space.6: 24px
  space.8: 34px
components:
  - card
  - balance-block
  - period-selector
  - category-row
  - bottom-nav
  - fab
  - honesty-banner
  - bottom-sheet
  - chip
  - keypad
  - list-row
  - secchiello-badge
---

## Brand & Style

> Canonical visual reference: [`mockups/direction-morbido.html`](mockups/direction-morbido.html). Tokens here are the source of truth; the mock illustrates the intended look.

mynance is a personal finance companion that has to do something most money apps avoid: surface uncomfortable truths — an unreconciled balance, a Secchiello that has slipped into the red, a Drift between what was planned and what was spent — without ever feeling like a bank or a scolding spreadsheet. The visual identity exists to make those truths land gently.

The chosen direction is **"Morbido"** (Italian for *soft*): calm, trustworthy, comfortable, warm and welcoming. The personality is pillowy — very rounded cards, airy spacing, a muted sage/teal accent that is never loud, and a large, friendly system sans with generous bold weights. It is explicitly **not** bank-cold and **not** harsh high-contrast. Where accessibility guidelines might push toward stark black-on-white, Morbido deliberately stays *legible-but-warm*: ink is a soft warm charcoal, never pure black; the canvas is a warm ivory, never clinical white.

The emotional contract is honesty without alarm. Reconciliation reminders, under-funded Secchielli and other honesty states are rendered in a warm amber (`color.honesty`) — clear and noticeable, but never the red of an error or a banking overdraft. The user should feel nudged by a trusted friend, not flagged by a system.

Theme support is first-class: light and dark are both designed, the **default follows the device/system setting**, and the user can manually override it. Both themes carry the same warmth — the dark mode is a warm dark brown, not a cold black.

## Colors

The palette is warm throughout. Every token is defined for both light and dark themes in the frontmatter; values are lifted directly from the Morbido source of truth.

- **`color.bg`** — the warm ivory canvas (light `#F4F1EA`) / warm dark brown (dark `#21201D`). Never pure white, never pure black.
- **`color.surface`** — the cream card surface (`#FBFAF6` / `#2C2A27`) that floats above the canvas. Carries the soft elevation shadow.
- **`color.surface-2`** — the inset/recessed surface (`#EFEAE0` / `#353230`) used for split cells, segmented controls, chips and keypad keys.
- **`color.ink`** — primary text (`#3A3A38` / `#ECE7DD`). A warm charcoal in light, a cream in dark — deliberately softened from pure values.
- **`color.ink-soft`** — secondary text, labels, inactive states (`#6D6A63` / `#A29D92`).
- **`color.accent`** — the muted sage/teal brand accent (`#7FA99B` / `#9CC4B5`). Reserved for **soft fills, progress bars and large display** (selected-chip rings, the category bar fill); never small text. Never squillante (never loud).
- **`color.accent-ink`** — the legible sage accent (`#527A6D` / `#9CC4B5`) for accent-colored **text/icons**, the **FAB fill**, and the **active bottom-nav indicator** — it clears contrast even with a white glyph.
- **`color.accent-soft`** — the tenuous sage fill (`#DDE8E2` / `#38463F`) for selected chips, the Secchiello badge background, the avatar.
- **`color.positive`** — the calm net-positive green (`#6B9B7C` / `#93C4A0`) reserved for **large display** (the hero positive Netto) and soft fills; never small text.
- **`color.positive-ink`** — the legible positive green (`#4D725A` / `#93C4A0`) for **small positive figures** (e.g. the Entrate value).
- **`color.negative`** — a **warm terracotta/clay** (`#A05C43` / `#D89479`) for a negative Netto. [ASSUMPTION: morbido mock shows no negative Netto; chose a warm-but-clear clay tone — distinct from positive green, harmonized with the amber honesty family, and explicitly NOT an alarm red.]
- **`color.honesty`** — warm amber (`#8B6237` / `#E0B080`) for the honesty banner text, icon and chevron. The signal color for uncomfortable truths.
- **`color.honesty-bg`** — the soft amber banner fill (`#F6E9D8` / `#423526`).
- **`color.bar-track`** — the unfilled portion of category progress bars (`#EAE4D8` / `#3A3733`). A color token only — the bar itself belongs to the `category-row` component.
- **`color.focus`** — the 2px focus-ring color (`#527A6D` / `#9CC4B5`). A dedicated token; it must **not** reuse the soft `color.accent`.

**Usage & contrast.** The `-ink` variants (`color.accent-ink`, `color.positive-ink`) are for **text, icons and small figures**, plus the **FAB fill** and the **active bottom-nav indicator**; the base variants (`color.accent`, `color.positive`) are for **soft fills, progress bars and large display only** (e.g. the hero Netto number), never small text. Splitting the palette this way keeps it warm — comfortable rather than clinical — while clearing **WCAG AA** in both light and dark themes.

## Typography

A single **system sans** stack (`font.sans`) carries the whole product — friendly, native to each platform, and never a corporate display face. Personality comes from size and weight, not from a custom typeface.

- **`type.display`** (~46px / 800, tight `-0.03em` tracking) — the hero Netto number on the balance block, and the large amount in the quick-add sheet.
- **`type.h1`** (~30px / 800, `-0.02em`) — screen titles.
- **`type.h2`** (~15–17px / 800) — card and section headings (e.g. "Spese per categoria").
- **`type.body`** (~15px / 500) — default text, category names, row content.
- **`type.caption`** (~12px / 600) — labels, meta fields, badges; often uppercase with wide letter-spacing for the all-caps eyebrow labels (e.g. "BILANCIO · GIUGNO", "CATEGORIA").

Three weights only: **`weight.regular` 500** (note: the regular weight is a medium 500, never a thin/light — it keeps text warm and grounded), **`weight.semibold` 700**, and **`weight.black` 800** reserved for hero numbers and headings. The generous use of 800 on numbers is what makes the app feel confident and friendly rather than fragile.

## Layout & Spacing

An **airy** spacing scale drives the whole layout — generous negative space is a core brand value, not a luxury.

Scale: `space.1` 4 · `space.2` 8 · `space.3` 12 · `space.4` 16 · `space.5` 20 · `space.6` 24 · `space.8` 34.

- Single-column, mobile-first. Cards are separated by `space.4` (16px) gaps and the scroll area carries roomy outer padding (~`space.5`/`space.8` horizontal, generous top inset below the notch).
- Card internal padding is large (~`space.6` and up) so content never touches the rounded edges.
- The largest gaps land between major surfaces; the smallest between tightly-related elements (e.g. a label above its value). Vertical rhythm stays loose — the screen is intentionally *non affollata* (uncluttered).
- Bottom nav reserves extra bottom padding for the home-indicator safe area.

## Elevation & Depth

Depth is soft and physical, never hard UI chrome.

- Floating cards (`card`, `balance-block`) sit on `color.surface` and carry a single **soft, low, warm-tinted drop shadow** — large blur, negative spread, low opacity, tinted toward the warm ink/brown rather than neutral grey (light `0 12px 28px -16px rgba(60,55,45,.35)`; dark deepens to `rgba(0,0,0,.55)`).
- Inset surfaces (`color.surface-2`) read as *recessed* — distinguished by tone, not by an inner shadow.
- The FAB and primary "Salva" button carry a **colored** accent-tinted shadow (a sage glow), reinforcing them as the hero actions.
- The bottom sheet floats with an upward shadow (`0 -16px 40px -18px`).
- Hierarchy comes primarily from rounding, tone and spacing; shadow is supportive, never the main signal.

## Shapes

Roundedness is the signature of Morbido — pillowy, soft, comfortable.

- **`radius.card` 34px** — the large floating cards (balance block, category card). Maximum coziness.
- **`radius.panel` 24px** — the honesty banner and secondary panels. The bottom sheet uses ~38px on its top corners as a larger sibling of this.
- **`radius.control` 18px** — keypad keys, meta tiles, segmented-control buttons, period buttons (~17–22px range).
- **`radius.pill` 999px** — fully-rounded elements: chips, the Secchiello badge, progress-bar tracks and fills, the FAB circle, the avatar.

No sharp corners exist anywhere in the product. Even small interactive elements are softened.

## Components

**`card`** — base floating container. `color.surface` fill, `radius.card` (34px), generous internal padding (~`space.6`), soft warm drop shadow. The structural unit of every screen.

**`balance-block`** — the hero card. Centered all-caps eyebrow label (`type.caption`, `color.ink-soft`, wide tracking, e.g. "BILANCIO · GIUGNO"); the Netto in `type.display` (large display) colored `color.positive` (positive) or `color.negative` (negative), prefixed with sign; below it a 12px-gap split of two inset cells (`color.surface-2`, `radius.control`+) showing Entrate (small value in `color.positive-ink`) and Spese (value in `color.ink`), each with a `type.caption` key over an ~17px / 800 value.

**`period-selector`** — segmented control on `color.surface-2`, `radius.panel`-ish (~22px), 5px padding. Four equal buttons (Giorno · Sett. · Mese · Anno); inactive in `color.ink-soft` 600; the active one lifts onto `color.surface` with `color.ink` 800 and a small soft shadow. Paired with a nav row below it (‹ month ›, arrows in `color.accent`, plus the profile avatar).

**`category-row`** — one Spesa category in the home list. Top line: emoji + name (`type.body`, `color.ink`) + optional `secchiello-badge` + amount (~14.5px / 800). Below it a full-width progress bar: track in `color.bar-track`, fill in `color.accent`, both `radius.pill`, ~11px tall, width proportional to spend. Rows sorted descending by total spend; tapping a row opens that category's detail. ~`space.4` gap between rows.

**`bottom-nav`** — five items on `color.surface` with a `color.surface-2` hairline top border, ~11px top / 16px bottom padding (safe area). Items: Mese · Statistiche · ＋ Aggiungi (center hero) · Liquidità · Altro. Each item is an icon (~21px) over a ~10.5px / 600 label in `color.ink-soft`; the active item switches to `color.accent-ink` (the active indicator).

**`fab`** — the central "Aggiungi" action inside the bottom nav. A 58px `color.accent-ink` circle, lifted ~26px above the bar (`margin-top:-26px`), white "＋" glyph (light) / dark glyph (dark) — the `color.accent-ink` fill keeps the white glyph legible — carrying a colored sage-glow shadow. Label "Aggiungi" in `color.accent-ink` 700 beneath. Opens the quick-add `bottom-sheet`.

**`honesty-banner`** — the warm-truth surface (FR-15/16: reconciliation, under-funded Secchiello). `color.honesty-bg` fill, 1px warm amber-tinted border, `radius.panel` (24px; ~20px when nested in the sheet), ~15px/18px padding. Layout: leading icon (⚠️ / 🪣), then text in `color.honesty` 600 with a `small` sub-line at reduced weight/opacity, then a trailing `›` chevron in `color.honesty` when tappable. Always amber — never alarm-red.

**`bottom-sheet`** — the quick-add surface, rising from the FAB. `color.surface` fill, ~38px top corners, ~18–22px padding, upward shadow; a scrim (`dim`) dims the screen behind it. Top: a centered grip pill (`color.surface-2`, `radius.pill`), a Spesa/Entrata segmented toggle, and a round close (✕) on `color.surface-2`. Then the amount in `type.display`-scale (~54px / 800) with a soft `color.ink-soft` currency mark, the CATEGORIA label + `chip` row, a row of three meta tiles (Data · Nota · Secchiello), the "Salva" button, and the `keypad`. Swipe-down to dismiss.

**`chip`** — pill selector for Categoria. Default: `color.surface-2` fill, `color.ink` text, `type.body`-ish (~13px / 600), `radius.pill`, ~9×15px padding. Selected: `color.accent-soft` fill, `color.ink` text at 800, with an inset 2px `color.accent` ring (the ring is a fill/decoration, so the soft accent is fine here). A "＋ altre…" overflow chip uses `color.ink-soft`.

**`keypad`** — 3-column numeric grid, 8px gaps. Each key is `color.surface-2`, `radius.control` (18px), ~14px vertical padding, ~21px / 700 `color.ink` digit text. Includes ",", "0", and "⌫". Appears immediately on sheet open for fast amount entry.

**`list-row`** — generic row pattern (meta tiles in the sheet, settings/detail rows). Label-over-value or label-left/value-right, `color.surface-2` background or hairline separation, `radius.control`, `type.caption` label in `color.ink-soft` over `type.body` value.

**`secchiello-badge`** — the small marker that tags a category/row as a Secchiello. `type.caption`-scale (~10px / 800), wide tracking, uppercase "SECCHIELLO", `color.accent` text on `color.accent-soft` fill, `radius.pill`, ~3×9px padding. Sits inline between the category name and amount.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Keep generous negative space; let cards breathe (*non affollata*) | Crowd the screen or compress to fit more in |
| Use warm ivory / warm dark-brown canvases and warm charcoal/cream ink | Use stark black-on-white or a cold corporate blue |
| Round everything — cards to `radius.card`, controls to `radius.control`, pills to 999px | Introduce sharp corners or hard rectangular UI |
| Surface uncomfortable truths (Riconciliazione, under-funded Secchiello, Drift) warmly in `color.honesty` amber | Use alarm-red or banking-overdraft red for honesty states |
| Use the muted sage sparingly — `color.accent-ink` for hero actions, active states, accent text/icons; `color.accent` for soft fills and large display | Make the accent loud (squillante), use it as decoration everywhere, or use the soft `color.accent` for small text |
| Reserve `weight.black` 800 for hero numbers and headings; keep regular text at a grounded 500 | Use thin/light weights that make text feel fragile or clinical |
| Let the soft, warm-tinted shadow imply gentle elevation | Stack hard drop shadows or use neutral-grey UI shadows |
| Honor the device/system theme by default, with manual override | Force a single theme or ship a cold black dark mode |
| Keep Italian domain terms verbatim (Secchiello, Liquidità, Spesa, Entrata, Categoria, Patrimonio, Cuscinetto, Drift) | Translate or rename domain terms in the UI |
