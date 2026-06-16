---
title: mynance — Accessibility Review (Morbido system)
status: draft
created: 2026-06-15
reviewer: accessibility audit
scope: DESIGN.md (palette light+dark, type) + EXPERIENCE.md (Accessibility Floor, states, primitives)
intent: verify the WARM "Morbido" palette stays usably legible; preserve warmth, flag only real breaks, propose minimal warm-preserving nudges.
---

# mynance — Accessibility Review

## Purpose and stance

This review respects the explicit product intent: the **"Morbido"** system is meant to be warm and soft, **not** harsh high-contrast, and the Accessibility Floor in `EXPERIENCE.md` (§Accessibility Floor) treats WCAG AA as a *floor on legibility met within the warm palette* — not a license to crank contrast to black-on-white. So the goal here is narrow: confirm the warmth is legible, and flag only the places where warmth actually drops below a usable threshold. Where a fix is needed, it is the **smallest warm nudge** that passes — same hue and saturation, just deepened a few percent in lightness. Nothing here proposes a colder or starker design.

Thresholds applied: **4.5:1** for normal body text, **3:1** for large text (≥ ~18.66px bold / ~24px regular — the hero `type.display` 46px/800, `type.h1` 30px/800, and most 800-weight values qualify as "large") and for non-text UI components / graphical objects (WCAG 1.4.11 — progress bars, focus rings, the FAB).

Contrast ratios below are computed with the WCAG 2.x relative-luminance formula from the exact hex tokens in `DESIGN.md`.

---

## 1. Headline verdict

**The dark theme is fully compliant and genuinely warm — no changes needed.** The **light theme is legible for all primary text** (`color.ink` is excellent everywhere) **but several warm mid-tone colors fall below their thresholds in light mode**: `color.accent` as a text/active color, `color.positive` as a value color, `color.honesty` at body-text size, and `color.ink-soft` for secondary text. These are all fixable with a 5–12% lightness drop that keeps the hue intact and the palette unmistakably Morbido.

---

## 2. Text & color contrast — measured, per pair

### 2.1 Light theme

| Foreground | Background | Ratio | Threshold | Result |
|---|---|---|---:|---|
| `color.ink` `#3A3A38` | `color.bg` `#F4F1EA` | **10.11:1** | 4.5 | PASS (excellent) |
| `color.ink` `#3A3A38` | `color.surface` `#FBFAF6` | **10.91:1** | 4.5 | PASS (excellent) |
| `color.ink` `#3A3A38` | `color.surface-2` `#EFEAE0` | **9.51:1** | 4.5 | PASS |
| `color.ink-soft` `#807C74` | `color.surface` `#FBFAF6` | **3.98:1** | 4.5 | FAIL as body · PASS as large/UI |
| `color.ink-soft` `#807C74` | `color.bg` `#F4F1EA` | **3.68:1** | 4.5 | FAIL as body · PASS as large/UI |
| `color.ink-soft` `#807C74` | `color.surface-2` `#EFEAE0` | **3.47:1** | 4.5 | FAIL as body · PASS as large/UI |
| `color.honesty` `#B07C45` | `color.honesty-bg` `#F6E9D8` | **3.02:1** | 4.5 | FAIL as body · PASS as large/UI |
| `color.positive` `#6B9B7C` | `color.surface` `#FBFAF6` | **3.04:1** | 4.5 | FAIL as body · PASS as large only |
| `color.positive` `#6B9B7C` | `color.surface-2` `#EFEAE0` | **2.65:1** | 3.0 | **FAIL even for large** |
| `color.positive` `#6B9B7C` | `color.bg` `#F4F1EA` | **2.82:1** | 3.0 | **FAIL even for large** |
| `color.negative` `#B0654A` | `color.surface` `#FBFAF6` | **4.18:1** | 4.5 | FAIL as body (marginal) · PASS as large |
| `color.negative` `#B0654A` | `color.surface-2` `#EFEAE0` | **3.64:1** | 4.5 | FAIL as body · PASS as large |
| `color.negative` `#B0654A` | `color.bg` `#F4F1EA` | **3.87:1** | 4.5 | FAIL as body · PASS as large |
| `color.accent` `#7FA99B` | `color.surface` `#FBFAF6` | **2.50:1** | 4.5 / 3.0 | **FAIL for text AND UI** |
| `color.accent` `#7FA99B` | `color.bg` `#F4F1EA` | **2.31:1** | 3.0 | **FAIL for UI graphic** |
| `color.accent` `#7FA99B` | `color.surface-2` `#EFEAE0` | **2.18:1** | 3.0 | **FAIL for UI graphic** |
| `color.accent` `#7FA99B` | `color.accent-soft` `#DDE8E2` | **2.08:1** | 4.5 / 3.0 | **FAIL** (selected-chip text) |
| white `#FFFFFF` glyph | `color.accent` `#7FA99B` (FAB ＋) | **2.61:1** | 3.0 | **FAIL** (FAB glyph) |

### 2.2 Dark theme — all pass

| Foreground | Background | Ratio | Result |
|---|---|---|---:|
| `color.ink` `#ECE7DD` | `color.bg` `#21201D` | **13.22:1** | PASS |
| `color.ink` `#ECE7DD` | `color.surface` `#2C2A27` | **11.61:1** | PASS |
| `color.ink` `#ECE7DD` | `color.surface-2` `#353230` | **10.33:1** | PASS |
| `color.ink-soft` `#A29D92` | `color.surface` `#2C2A27` | **5.30:1** | PASS (body) |
| `color.ink-soft` `#A29D92` | `color.bg` `#21201D` | **6.03:1** | PASS |
| `color.ink-soft` `#A29D92` | `color.surface-2` `#353230` | **4.71:1** | PASS (body) |
| `color.honesty` `#E0B080` | `color.honesty-bg` `#423526` | **6.04:1** | PASS (body) |
| `color.positive` `#93C4A0` | `color.surface` `#2C2A27` | **7.25:1** | PASS |
| `color.positive` `#93C4A0` | `color.surface-2` `#353230` | **6.45:1** | PASS |
| `color.positive` `#93C4A0` | `color.bg` `#21201D` | **8.26:1** | PASS |
| `color.negative` `#D89479` | `color.surface` `#2C2A27` | **5.75:1** | PASS (body) |
| `color.negative` `#D89479` | `color.surface-2` `#353230` | **5.11:1** | PASS (body) |
| `color.negative` `#D89479` | `color.bg` `#21201D` | **6.54:1** | PASS |
| `color.accent` `#9CC4B5` | `color.surface` `#2C2A27` | **7.48:1** | PASS |
| `color.accent` `#9CC4B5` | `color.bg` `#21201D` | **8.52:1** | PASS |
| `color.accent` `#9CC4B5` | `color.surface-2` `#353230` | **6.65:1** | PASS |
| `color.accent` `#9CC4B5` | `color.accent-soft` `#38463F` | **5.19:1** | PASS (body) |
| dark glyph `#21201D` | `color.accent` `#9CC4B5` (FAB ＋) | **8.52:1** | PASS |

The dark theme is exemplary: it is warm (the brown `#21201D` canvas, cream ink) **and** clears AA everywhere, including the amber honesty signal at body size (6.04:1). No dark-theme changes are recommended. This proves the warm direction and AA are not in conflict — the light theme simply was not tuned as carefully.

---

## 3. Findings (severity-ordered)

### HIGH — `color.accent` is illegible as a text/active color in light theme
`color.accent` `#7FA99B` is specified (DESIGN.md §Colors, `period-selector`, `bottom-nav` active item, `secchiello-badge` text, selected `chip` text at 800, the FAB "Aggiungi" label) as both an active-state **text** color and a UI graphic. Against every light background it ranges **2.08–2.50:1** — below even the 3:1 UI floor. Concretely affected:
- **Active `bottom-nav` item** turns `color.accent` (the only signifier of "which tab am I on") — 2.50:1 on surface. The active state is hard to perceive.
- **Selected `chip`** uses `color.accent` text on `color.accent-soft` — **2.08:1**, the worst pair in the system. The selected category in quick-add is barely distinguishable from the chip fill.
- **`secchiello-badge`** — `color.accent` 800 on `color.accent-soft` — same 2.08:1.
- **FAB white ＋ glyph** on `color.accent` — 2.61:1, below the 3:1 needed for the icon to be perceivable.
- **Progress-bar fill** (`category-row`) — `color.accent` fill on `color.bar-track` `#EAE4D8` is also very low (the fill is a meaningful graphical object showing spend proportion).

**Minimal warm fix (keep sage hue/saturation, deepen lightness):**
- A single deepened accent text/active token, e.g. **`#527A6D`** (same hue, L 40%) → 4.61:1 on surface, 4.5:1 on accent-soft — passes as text everywhere it is used as text. This is still a muted, never-squillante sage.
- Where `color.accent` is only a **graphic** (progress-bar fill, FAB circle), 3:1 suffices: **`#6A9B8A`** → ~3.0:1 on surface/track and stays closer to the original. Or simply reuse the deeper `#527A6D` for both — it remains soft.
- **FAB glyph:** swap the white ＋ for the same dark glyph the dark theme already uses (`#21201D` on accent = 8.52:1 in dark; on the deepened light accent it likewise clears 3:1), OR keep white on the deepened accent — verify ≥3:1.
- Note: the *selected-chip* state also carries an "inset 2px `color.accent` ring" (DESIGN.md `chip`); deepening the ring color is the cheapest way to keep the selected state perceivable even before text contrast is addressed.

### HIGH — `color.positive` fails as a value color in light theme (and fails even the large threshold on bg / surface-2)
`color.positive` `#6B9B7C` is the color of the **positive Netto hero number** and **Entrate values** (`balance-block`, DESIGN.md). On `color.surface` it is **3.04:1** — the hero `type.display` (46px/800) just scrapes the 3:1 large-text bar, but the smaller Entrate value (~17px/800) does not reliably qualify as "large," and on `color.bg` (**2.82:1**) and `color.surface-2` (**2.65:1**, the inset Entrate cell) it **fails even the 3:1 large threshold**. The Entrate value sits in a `color.surface-2` inset cell per the `balance-block` spec — that is the 2.65:1 case, the second-worst pair in the system.

**Minimal warm fix:** deepen to **`#4D725A`** (same green hue/saturation, L ~37%) → 4.53:1 on surface-2, ≥4.5:1 on surface and bg. Still a calm, non-alarm green. This single token replaces `#6B9B7C` in light mode for *value text*; the lighter tone could be retained only for large decorative fills if any exist (none identified).

### MEDIUM — Amber honesty `color.honesty` fails at body size in light theme
`color.honesty` `#B07C45` on `color.honesty-bg` `#F6E9D8` is **3.02:1**. This is fine for the banner's large/bold lead text, but the `honesty-banner` spec includes a **`small` sub-line at reduced weight/opacity** (DESIGN.md `honesty-banner`), and honesty messages like `Secchiello in rosso di X €` / `Scostamento: −87 €` are the *entire point* of the product (EXPERIENCE.md §Honesty & Surfacing) — they must be readable, and the Accessibility Floor explicitly says so ("warnings must be readable, that is the whole point"). Body-size amber at 3.02:1 does not meet AA, and the reduced-opacity sub-line will be worse.

**Minimal warm fix:** deepen the light-mode honesty *text* token to **`#8B6237`** (same amber hue, L ~38%) → **4.5:1** on `honesty-bg`. Keep `color.honesty-bg` unchanged (the soft fill is fine). The dark theme already passes (6.04:1), so this is a light-only nudge. Crucially this stays amber, not red — it does not violate the "never alarm-red" rule (DESIGN.md Do/Don't, EXPERIENCE.md State Patterns).

### MEDIUM — `color.ink-soft` secondary text fails AA body in light theme
`color.ink-soft` `#807C74` is **3.47–3.98:1** across light backgrounds — below 4.5:1. This token carries a lot of real text: `type.caption` labels, all-caps eyebrows ("BILANCIO · GIUGNO", "CATEGORIA"), `bottom-nav` inactive labels, `period-selector` inactive labels, meta-tile labels, the "＋ altre…" overflow chip, and `list-row` labels. Many are bold/caps and arguably "large," but caption text at 12px/600 is borderline at best and the body row labels are not large. The Accessibility Floor *claims* `color.ink-soft` "clear[s] AA on surface/bg" (EXPERIENCE.md §Accessibility Floor) — **this claim is inaccurate in light theme** and should be corrected or the token deepened.

**Minimal warm fix:** deepen to **`#6D6A63`** (same warm-grey hue, L ~41%) → 4.50:1 on surface-2, ≥4.5:1 on surface and bg. Barely perceptible shift, fully preserves the soft secondary-text feel. Dark `color.ink-soft` already passes (4.71–6.03:1) — light-only.

### LOW — `color.negative` is marginal as body text in light theme
`color.negative` `#B0654A` (warm clay, the negative-Netto color) is **3.64–4.18:1** in light. The negative Netto is rendered in `type.display` (large) so it passes as-is for its primary use. But if the clay is ever used at body size (signed figures in lists, a negative signed value in a `list-row`), it falls short.
**Minimal warm fix (only if used below large size):** **`#A05C43`** (same clay hue, L ~44%) → 4.53:1 on bg, 4.56:1 on surface. If `color.negative` is *only ever* the large hero Netto, no change is required. Worth a one-line clarification in DESIGN.md that the clay is large-text-only in light theme.

### PASS / NOTE — non-color signifiers for honesty states are adequate
Honesty states are **not** conveyed by amber alone, which is correct:
- `honesty-banner` pairs the amber with a **leading icon (⚠️ / 🪣)**, **text**, and a **chevron** (DESIGN.md `honesty-banner`).
- Under-funding carries an explicit **textual** message (`Secchiello in rosso di X € — la Quota salirà per recuperare`) and the **negative number itself** (EXPERIENCE.md State Patterns, Voice & Tone).
- Drift shows a **signed magnitude** (`Scostamento: −87 €`) plus text.
- Cuscinetto breach is a **sentence** (`Risparmio libero sotto il Cuscinetto di sicurezza`).
No state relies on color alone. Good. (The only ask is the MEDIUM fix above so the amber text is *readable*, not that it needs another signifier.)

### PASS / NOTE — positive/negative Netto sign is never color-alone
EXPERIENCE.md §Accessibility Floor: "Sign is never conveyed by color alone — `color.positive`/`color.negative` always pair with a `+`/`−` and the figure." The `balance-block` spec prefixes the Netto with its sign. Compliant. (Still fix the *contrast* of `color.positive` per HIGH above so the number is legible, but the sign-encoding itself is fine.)

---

## 4. Interaction, focus, targets — review against the Floor

- **Tap targets ≥ 44px** — the Floor states this explicitly for "every chip, row, nav slot, keypad key" (EXPERIENCE.md §Accessibility Floor; §Component Patterns). DESIGN.md gives `keypad` keys ~14px vertical padding on a 3-col grid and `chip` ~9×15px padding — these are *visual* paddings, not guaranteed hit areas. **Action: confirm the rendered hit-area (not just the inked pill) is ≥44×44px**, especially for `chip` (small pills) and the `keypad` "," / "⌫" keys, and the period-selector's four buttons. The intent is documented; verify it survives implementation. The FAB at 58px is fine.

- **Visible focus indicator** — required on every interactive element with traversal in reading order (Floor). DESIGN.md does **not** define a focus-ring token or its color/contrast. **Action: define a focus-ring token that itself meets 3:1 against adjacent colors in BOTH themes.** Do not rely on `color.accent` for the light-mode ring (it is 2.5:1 — see HIGH); use the deepened accent or `color.ink`. This is the single biggest documentation gap for keyboard/switch users.

- **Numeric keypad & bottom-sheet usability** — keypad-up-on-open and amount-first is good for one-handed entry (EXPERIENCE.md Flow 0, Interaction Primitives). Concerns: (a) **swipe-down to dismiss** the sheet must have a non-gesture equivalent — the spec does include a **round close (✕)** button, good; ensure that ✕ on `color.surface-2` is itself ≥3:1 and ≥44px. (b) The sheet should **trap focus** and restore focus to the FAB on close (not stated — add to the Floor). (c) `Salva` button uses the accent glow; verify the button **label** contrast (text on accent) meets 4.5:1 — same accent issue as HIGH. (d) Reduce-Motion handling for the sheet rise is correctly specified (Floor: "skip sheet-rise and toast fades").

- **Period-selector & chips** — the active period button "lifts onto `color.surface` with `color.ink` 800" (10.9:1, great) while inactive is `color.ink-soft` (the MEDIUM contrast issue). Active vs inactive is distinguished by **elevation + tone**, not color alone — good for color-blind users. For `chip`, selected vs unselected relies on fill + the 2px accent ring + text weight; the ring/text contrast is the HIGH issue, but the **shape/weight** difference is a non-color signifier, so selection is not *color-alone*. Fix the accent contrast and this is solid.

- **Dynamic type** — Floor requires honoring system text-size without truncation. The fixed px values in DESIGN.md (e.g. `type.caption` 12px) should be rem/scalable; the four-button `period-selector` and chip row are the truncation risks at the largest setting. Documented intent is correct; verify in build.

- **Screen-reader** — Floor specifies role+state labels, banner/toast live-region announcements, Italian terms read verbatim. Well-specified. One add: the **honesty-banner and save-toast** announcements should use an appropriate `aria-live` politeness (toast = polite, reconciliation-due banner = polite, not assertive, to honor the "never nag" tone).

---

## 5. Summary of recommended changes (light theme only; warmth preserved)

All fixes keep the original hue and saturation and only deepen lightness. Dark theme: no changes.

| Token (light) | Current | Issue | Proposed warm nudge | New ratio |
|---|---|---|---|---|
| `color.accent` (as text/active) | `#7FA99B` | 2.08–2.50:1, illegible active state | `#527A6D` | ≥4.5:1 text |
| `color.accent` (as graphic only) | `#7FA99B` | <3:1 bar/FAB | `#6A9B8A` (or reuse `#527A6D`) | ~3.0:1 |
| `color.positive` (value text) | `#6B9B7C` | 2.65–3.04:1 | `#4D725A` | ≥4.5:1 |
| `color.honesty` (text) | `#B07C45` | 3.02:1 body | `#8B6237` | 4.5:1 |
| `color.ink-soft` | `#807C74` | 3.47–3.98:1 | `#6D6A63` | ≥4.5:1 |
| `color.negative` (only if body-size) | `#B0654A` | 3.64–4.18:1 | `#A05C43` | ≥4.5:1 |

Documentation fixes:
1. Correct the Accessibility Floor claim that `color.ink-soft` "clears AA on surface/bg" — it does not in light theme until deepened.
2. Define a **focus-ring token** with stated ≥3:1 contrast in both themes.
3. Add **focus-trap + focus-restore** to the bottom-sheet behavior.
4. Note that light-mode `color.negative` and the *lighter* `color.positive`/`color.accent` are **large-text/graphic only** if those tones are retained anywhere.

None of these change the Morbido character: the canvases, ink, surfaces, radii, spacing, dark theme, and the amber-not-red honesty rule all stay exactly as designed. The nudges only deepen four warm mid-tones in light mode by a few percent so the warmth is *readable* — which is precisely what the Accessibility Floor already commits to.
