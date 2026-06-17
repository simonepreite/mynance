# Spine Pair Review — mynance UX (rubric walker)

- **DESIGN.md:** `c:\Users\simone.preite_dinova\Desktop\CLIENTI\GIT\mynance\_bmad-output\planning-artifacts\ux-designs\ux-mynance-2026-06-15\DESIGN.md`
- **EXPERIENCE.md:** `c:\Users\simone.preite_dinova\Desktop\CLIENTI\GIT\mynance\_bmad-output\planning-artifacts\ux-designs\ux-mynance-2026-06-15\EXPERIENCE.md`
- **Run at:** 2026-06-15
- **Gate verdict:** PASS-WITH-FIXES

## Overall verdict

This is a strong, downstream-ready spine pair. Every IA surface in the bottom-nav is specified, every PRD FR (FR-1..FR-22) and user journey (UJ-1..UJ-4 plus the hero quick-capture) maps to a surface, the honesty principle is carried consistently across DESIGN and EXPERIENCE, and the token cross-reference integrity is clean — every `{token}` referenced in EXPERIENCE.md resolves to a DESIGN.md frontmatter token, and no design hex is inlined in the behavioral spine. A consumer (architect or story-dev) can source-extract cleanly. The shortfalls are minor and mostly about closing small gaps: two component-like names used in prose but absent from the `components` namespace, a couple of states left implicit (offline, permission/recovery-failure), and a few load-bearing contrast pairings asserted rather than stated as concrete targets.

## 1. Coverage (IA surfaces + PRD FRs) — Pass

Checked: every `bottom-nav` slot (Mese, Statistiche, Aggiungi, Liquidità, Altro) has a behavioral section; Riconciliazione (no nav icon) is explicitly handled as a contextual banner + Altro entry; Onboarding/registration is specified; the Impostazioni sub-surfaces (Categorie, Regole ricorrenti, Liquidità iniziale, Account & recovery) are each present. PRD features §4.1–§4.6 and FR-1..FR-22 are each mapped (confirmed against the coverage self-check at lines 213–217 and spot-checked against the body: FR-9 Quota auto-compute, FR-10 no-clamp under-funding, FR-15 Cuscinetto, FR-16–18 reconciliation/Drift, FR-19–22 Patrimonio). No orphan FR found.

### Findings
- **low** Statistiche is the thinnest surface relative to its FR coverage claim (§4.2/§4.4 "read views") — it names line trends + a pie but does not specify empty/no-data behavior for charts (location: EXPERIENCE.md lines 32, 51). *Fix:* add a one-line empty/insufficient-data treatment for Statistiche to State Patterns ("not enough history to chart yet").

## 2. Clarity & testability of behavior — Pass

Behavioral rules are concrete and testable: the quick-capture optimal path is "three taps, keypad already up" (line 168, 173–176); Quota is "auto-computed and read-only" with the formula `max(0,(620−Saldo)/mesi)` (line 49, 184); recurring rules "auto-generate up to today only (no future/phantom items)" and "skipping does not create Drift" (line 59); reconciliation "fires only after the configured interval (default weekly)" (line 55). These are assertions a QA/ATDD author can turn into checks.

### Findings
- **low** "compute sub-second (NFR §10)" (line 111) is a borrowed NFR, not a UX-testable behavior in this doc; harmless but it leans on the PRD. *Fix:* none required — acceptable as context.

## 3. DESIGN ↔ EXPERIENCE token cross-reference integrity — Pass

Extracted all 14 unique `{token}` references in EXPERIENCE.md (`radius.card`, `color.accent`, `font.sans`, `type.display`, `color.honesty`, `color.honesty-bg`, `color.positive`, `color.negative`, `type.body`, `color.surface-2`, `color.ink`, `color.ink-soft`, `color.surface`, `color.bg`). **Every one resolves to a DESIGN.md frontmatter token.** No inlined design hex in EXPERIENCE.md — the only `#`-value is `#000` at line 134, used illustratively ("warm near-black, not pure `#000`"), which is correct usage, not a smuggled token. Clean.

## 4. State coverage (loading / empty / error / honesty) — Partial

State Patterns (lines 109–121) covers Loading (skeleton), three Empty variants (new account, no Spese, no Secchielli), Error (warm message + retry), Focus, and all three honesty states (under-funding, Drift/reconciliation-due, Cuscinetto breach) — with verbatim microcopy. Honesty coverage is exemplary and gets its own dedicated section (lines 144–152). The gap is two states that apply to this product but are not walked.

### Findings
- **medium** No **offline** state, despite this being responsive web with live-derived figures (Liquidità, Quota, Saldo) (location: State Patterns lines 109–121). *Fix:* add an offline/stale-data row ("showing last-known figures; reconnect to refresh").
- **medium** No **recovery-failure / wrong-credentials / lost-recovery-code** state, even though FR-1..FR-3 auth and the one-time recovery code are explicitly in scope and recovery is the only account-restore path (location: Onboarding lines 61, 63; Account & recovery line 61). *Fix:* add a State Patterns row for failed login and unavailable recovery code (warm copy, no scolding).
- **low** No empty/insufficient-data state for Statistiche charts (see Finding 1). *Fix:* as above.

## 5. Accessibility floor presence — Pass

A dedicated Accessibility Floor section (lines 132–142) states a real floor: WCAG AA as a legibility floor met within the warm palette; tap targets ≥44px; visible focus on every interactive element with reading-order traversal; sign never conveyed by color alone (always paired with +/− and figure); SR labels with role+state, banner/toast announce-on-appearance; dynamic type honored with no control truncation; Reduce Motion handling. This is concrete and resolves the warm-vs-contrast tension deliberately rather than hand-waving it.

### Findings
- **medium** AA is asserted for `{color.ink}`/`{color.ink-soft}` on surface/bg and for `{color.honesty}` on `{color.honesty-bg}`, but no concrete contrast ratios/targets are stated for these load-bearing pairs in either spine (location: EXPERIENCE.md lines 134, 138; DESIGN.md line 99 "comfortable rather than maximal"). The warm palette is precisely where AA is most at risk (e.g. `color.ink-soft #807C74` on `color.surface #FBFAF6`, `color.honesty #B07C45` on `color.honesty-bg #F6E9D8`). *Fix:* state the target ratio (e.g. "AA 4.5:1 for body, 3:1 for large/caption") and flag the at-risk pairs for verification, or add measured ratios to DESIGN.md Colors.

## 6. Voice/tone concreteness — Pass

Voice and Tone (lines 65–86) is concrete and testable: a Do/Don't table contrasting verbatim good vs bad strings, plus eight verbatim microcopy seeds keyed to specific states (empty, reconciliation banner, under-funding, Cuscinetto breach, Drift, save toast). The honesty-as-tone-rule and the anti-gamification stance (no streaks/badges, SM-C1/SM-C2) are explicit. EXPERIENCE.md prose stays behavioral; editorial voice lives in DESIGN.md. No issue.

## 7. Key-flow completeness (climax beats) — Pass

Five flows, each with a named protagonist verbatim from the PRD (Marco, Elena), numbered steps, and an explicit **Climax** beat: Flow 0 quick-capture (climax = quiet toast + Home already updated, three taps), Flow 1/UJ-1 (climax = €620 visibly spoken-for), Flow 2/UJ-2 (climax = close the gap in one action), Flow 3/UJ-3 (climax = committed vs free vs Cuscinetto at a glance), Flow 4/UJ-4 (climax = one believable Patrimonio total). Failure path present where applicable (Flow 0 wrong-Secchiello override; Flow 2 acknowledge-and-leave-open alternative).

### Findings
- **low** Flow 4 (UJ-4) is intentionally "lighter" with only a climax and no resolution/failure beat (line 206–209) — defensible for a read-only review flow, but the asymmetry is worth a deliberate note. *Fix:* none required; the "(lighter)" tag already signals intent.

## 8. Internal consistency — Pass (with one namespace nit)

Decision-log references (#2..#27) are used consistently; domain terms (Secchiello, Liquidità, Quota, Saldo, Patrimonio, Drift, Cuscinetto) are verbatim and identical across both spines and the Do/Don't tables; the honesty-amber-never-alarm-red rule is stated identically in DESIGN.md (Brand & Style, Do's/Don'ts) and EXPERIENCE.md (State Patterns, Honesty & Surfacing). `{color.negative}` is consistently reserved for negative Netto, not warnings, in both files.

### Findings
- **medium** `bar-track` is used as a component-style backtick name in EXPERIENCE.md (line 96, "a proportional `bar-track` bar") but is **not** in the DESIGN.md `components` frontmatter list — it exists only as the `color.bar-track` token and as a sub-element of `category-row`. *Fix:* either reference it as part of `category-row`'s progress bar or add `bar-track` to the component namespace; don't backtick a non-component.
- **low** DESIGN.md line 128 lists `cats` alongside `card`/`balance-block` as a floating card, but `cats` is not in the `components` frontmatter list and appears nowhere in EXPERIENCE.md. *Fix:* rename to `card` (the category card is just a `card` instance) or add it to the namespace.

## 9. Downstream-readiness for design/build — Pass

The pair is consumable: all color tokens carry light/dark hex pairs in frontmatter; component visual specs (DESIGN.md Components) pair with behavioral specs (EXPERIENCE.md Component Patterns) for each named component; the spine-wins-on-conflict rule is stated (line 15, 41); ASSUMPTION tags mark derived-not-decided choices (negative color, desktop quick-add panel). An architect/story-dev can extract IA, states, flows, and tokens without guessing.

### Findings
- **low** Composition references point at `.working/home-mese.v2.md` and `.working/quick-add.v1.md` (line 41) rather than a `mockups/`/`wireframes/` directory; ensure those `.working/` files travel with the artifact so the links don't dangle for downstream consumers. *Fix:* confirm the referenced `.working/` files are committed alongside the spine.

## Mechanical notes

- **Token refs:** 14/14 unique `{token}` references in EXPERIENCE.md resolve to DESIGN.md frontmatter. No inlined hex (only illustrative `#000`).
- **Component namespace:** 12 components declared in DESIGN.md frontmatter; all 12 are used in both spines. Two stray backtick names — `bar-track` (EXPERIENCE.md L96) and `cats` (DESIGN.md L128) — are not declared components (see §8).
- **Shape fit:** DESIGN.md sections are in canonical order (Brand & Style → Colors → Typography → Layout & Spacing → Elevation & Depth → Shapes → Components → Do's and Don'ts). EXPERIENCE.md carries all required defaults (Foundation, IA, Voice and Tone, Component Patterns, State Patterns, Interaction Primitives, Accessibility Floor, Key Flows) plus justified extras (Honesty & Surfacing, Responsive & Platform). Inspiration section absent but defensible — direction "Morbido" is the source of truth, no reference-product comparison is load-bearing.
- **Frontmatter:** both files have title/status/created/updated; EXPERIENCE.md `sources` resolve to the PRD, decision-log, and two `.working/` composition files.
