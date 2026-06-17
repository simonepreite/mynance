---
baseline_commit: 389afd1
---

# Story 1.6: Minimal onboarding shell and empty themed Home (UX-DR10)

Status: done

## Story

As a newly registered Utente, I want a minimal onboarding that lands me in an empty, themed app with gentle first-run guidance, so that I can start using mynance immediately without a heavy setup burden.

## Acceptance Criteria

- **AC1 — skippable onboarding step:** after the recovery code is saved, one light, recommended-but-skippable step ("Imposta la tua Liquidità iniziale per cominciare.") is offered, settable later from Impostazioni. *(The Liquidità iniziale value itself is wired to persistence in Story 2.2; this story delivers only the skippable shell + copy.)*
- **AC2 — land on empty Home + bottom-nav shell:** completing/skipping onboarding lands on an empty Home ("Mese") rendered with Morbido components and the `bottom-nav` shell (five slots present, destinations stubbed for later epics).
- **AC3 — calm empty state:** the empty Home shows calm first-run microcopy ("Imposta la tua Liquidità iniziale per cominciare.", "Ancora nessuna spesa questo mese.") with no false bars, no zero-state chart noise, no streaks/badges/exclamation marks.
- **AC4 — empty isolated dataset:** a brand-new account's Home reflects an empty, isolated dataset (no other Utente's data), consistent with Story 1.5.
- **AC5 — a11y floor:** focus ring, ≥44px tap targets, reading-order traversal, AA contrast (Story 1.2) hold throughout; every interactive element is labeled with role + state.

## Tasks / Subtasks

- [x] **Mobile-first app shell (AC2):** rewrote `_layout` into a `TopBar` + scrollable `<main>` + fixed `AppBottomNav`, replacing the template desktop sidebar. [frontend/src/routes/_layout.tsx, frontend/src/components/Common/TopBar.tsx, frontend/src/components/Common/AppBottomNav.tsx]
- [x] **Bottom-nav 5 slots + central ＋ (AC2):** Home · Liquidità · ＋ (Aggiungi) · Statistiche · Patrimonio, wired onto TanStack Router (active slot from pathname); the ＋ FAB opens a calm quick-add stub (bottom-sheet lands in 2.7). [frontend/src/components/Common/AppBottomNav.tsx]
- [x] **Stubbed destinations (AC2):** calm "in arrivo" placeholder screens for Liquidità, Statistiche, Patrimonio via a shared `ComingSoon`. [frontend/src/components/Common/ComingSoon.tsx, frontend/src/routes/_layout/{liquidita,statistiche,patrimonio}.tsx]
- [x] **Empty Home "Mese" + skippable onboarding prompt (AC1, AC3):** month-labelled empty Home with a dismissible first-run prompt ("Imposta la tua Liquidità iniziale…" → Impostazioni / Più tardi, dismissal persisted in localStorage) and a calm empty Spese state. [frontend/src/routes/_layout/index.tsx]
- [x] **Account access relocated (AC5):** username, Categorie, Impostazioni, theme, and logout moved into the TopBar account menu (Categorie under Impostazioni per UX-DR9). Removed the template Sidebar (AppSidebar/Main/User). [frontend/src/components/Common/TopBar.tsx]

## Dev Notes

- Onboarding is intentionally minimal (SM-C1 / entry-burden): the recovery-code "save now" panel (Story 1.3) plus one dismissible Home prompt. No dedicated onboarding route — the prompt is the "one light step", skippable and re-accessible via Impostazioni.
- The morbido components (`BottomNav`, `Card`, etc.) already carry the Story 1.2 a11y floor (≥44px `data-tap-target`, focus ring, text-safe `-ink` tokens / AA contrast); new interactive elements add explicit `aria-label`/`aria-current`.
- 1.6 fetches no money data — the empty/isolated dataset (AC4) is the natural state; real per-period aggregation arrives with Home "Mese" (Story 2.8).
- The template `Items` demo route remains but is unlinked (no nav slot); it will be superseded by Movimenti in Epic 2.

### Completion Notes List

_Frontend-only story. Verified locally (Node 22 + npm toolchain): `biome ci .` clean, `tsc -p tsconfig.build.json` + `vite build` green. The Morbido theme/component Playwright e2e runs in CI (browser download is blocked locally by the corporate proxy); the new shell reuses the floor-compliant morbido components and adds labeled controls._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | Mobile-first shell: TopBar + 5-slot bottom-nav (＋ quick-add stub) + ComingSoon stubs (Liquidità/Statistiche/Patrimonio) + empty themed Home "Mese" with skippable Liquidità-iniziale prompt; removed template Sidebar. Story done. |

### File List

**Added:** `frontend/src/components/Common/TopBar.tsx`, `frontend/src/components/Common/AppBottomNav.tsx`, `frontend/src/components/Common/ComingSoon.tsx`, `frontend/src/routes/_layout/liquidita.tsx`, `frontend/src/routes/_layout/statistiche.tsx`, `frontend/src/routes/_layout/patrimonio.tsx`
**Modified:** `frontend/src/routes/_layout.tsx` (mobile-first shell), `frontend/src/routes/_layout/index.tsx` (empty Home Mese + onboarding prompt), `frontend/src/routeTree.gen.ts`, `_bmad-output/implementation-artifacts/sprint-status.yaml`
**Removed:** `frontend/src/components/Sidebar/AppSidebar.tsx`, `frontend/src/components/Sidebar/Main.tsx`, `frontend/src/components/Sidebar/User.tsx`
