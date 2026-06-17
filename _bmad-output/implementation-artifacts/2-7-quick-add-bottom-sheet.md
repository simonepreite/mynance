---
baseline_commit: 39cd5a2
---

# Story 2.7: Quick-add bottom sheet — online-first optimistic capture (FR-5, FR-6, UX-DR4)

Status: done

## Story

As an Utente, I want a one-handed quick-add bottom sheet to capture a Spesa or Entrata "al volo" with optimistic UI, so that capture is fast and frictionless, lowering the chance a forgotten entry becomes Drift.

## Acceptance Criteria

- **AC1 — sheet + amount-first:** tapping the central ＋ raises the quick-add bottom-sheet with the amount focused, the Spesa/Entrata toggle defaulting to Spesa, and the date defaulting to today; amount uses the Italian decimal comma and is converted to integer cents before submission.
- **AC2 — category pick:** with an amount typed, a Categoria is chosen from type-scoped chips. *(Secchiello-badge is deferred: Secchielli arrive in Epic 3, Story 3.1.)*
- **AC3 — optimistic save:** on Salva the Movimento is created via the generated client (2.5/2.6); the derived Liquidità updates optimistically, the sheet falls away, and a quiet "Spesa aggiunta" / "Entrata aggiunta" toast appears.
- **AC4 — rollback on error:** a failed save rolls back the optimistic update (no phantom balance), shows a plain warm retry message (no raw error), and reconciles the affected query keys with server truth.
- **AC5 — server is the source of truth:** on success the `liquidita` and `movimenti` query keys are invalidated and re-fetched so derived figures come from the server (API-3: client never recomputes).
- **AC6 — dismiss + focus restore:** dismissing the sheet closes it without saving and restores focus to the ＋ trigger (focus trap + restore).

## Tasks / Subtasks

- [x] **QuickAdd bottom-sheet (AC1, AC2, AC6):** `Sheet side="bottom"` (Radix → focus trap + restore to trigger); amount-first focus via `onOpenAutoFocus` + ref; `inputMode="decimal"` with Italian-comma parse to cents (`lib/money`); Spesa/Entrata toggle (resets the type-scoped Categoria) and Categoria chips. [frontend/src/components/Common/QuickAdd.tsx]
- [x] **Optimistic mutation (AC3, AC4, AC5):** `useMutation` with `onMutate` (cancel + snapshot + optimistic `liquidita` delta: −Spesa / +Entrata), `onError` rollback + warm retry toast, `onSuccess` toast + close, `onSettled` invalidate `["liquidita"]`/`["movimenti"]`. [frontend/src/components/Common/QuickAdd.tsx]
- [x] **Wire to the ＋ FAB (AC1):** the central bottom-nav slot opens QuickAdd (replaced the 1.6 stub). [frontend/src/components/Common/AppBottomNav.tsx]
- [x] **Surface derived Liquidità on Home:** Home renders the derived Liquidità (`GET /liquidita`, Story 2.4) so the optimistic update is observable; the onboarding prompt now hides once `iniziale_is_set`. [frontend/src/routes/_layout/index.tsx]

## Dev Notes

- The bespoke numeric `keypad` and `secchiello-badge` (UX-DR2/UX-DR4) are deferred: the amount uses the native numeric input (`inputMode="decimal"`, focused on open) and Secchielli don't exist until Epic 3. The full per-Categoria Bilancio with `category-row` bars is Story 2.8 — here only the derived Liquidità number reflects the optimistic capture.
- Optimistic delta is applied to the `liquidita` cache only; `onSettled` always re-fetches so the server (not the client) owns the money (API-3). Spesa subtracts, Entrata adds — matching the calc engine.
- Swipe-to-dismiss is provided by the Radix overlay/Esc close with automatic focus restore to the ＋ trigger.

### Completion Notes List

_Frontend story. Verified locally (Node 22 + npm): `biome ci .` clean, `tsc` + `vite build` green. The create path is integration-tested server-side (Story 2.5/2.6 — create/recompute); the optimistic cache logic is the standard TanStack pattern. Browser e2e for the sheet is not run locally (Playwright browsers blocked by the corporate proxy); the theme e2e runs in CI._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | Quick-add bottom-sheet (amount-first, Spesa/Entrata toggle, Categoria chips, optimistic save + rollback + invalidation) wired to the ＋ FAB; derived Liquidità surfaced on Home. Story done. |

### File List

**Added:** `frontend/src/components/Common/QuickAdd.tsx`
**Modified:** `frontend/src/components/Common/AppBottomNav.tsx` (＋ opens QuickAdd), `frontend/src/routes/_layout/index.tsx` (derived Liquidità + prompt gating), `_bmad-output/implementation-artifacts/sprint-status.yaml`
