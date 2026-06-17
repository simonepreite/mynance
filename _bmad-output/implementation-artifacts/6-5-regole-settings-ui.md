---
baseline_commit: 9b21d88
---
# Story 6.5: Regole ricorrenti settings UI (UX-DR9, FR-8)
Status: done

## Summary
- Impostazioni → Regole ricorrenti (/regole, linked from Impostazioni): list of regole (amount € Italian locale, periodicità, day-of-period, kind/target), create form (amount €→cents, periodicità + custom interval, day-of-period, kind toggle Entrata/Versamento PAC with the matching target — Entrata Categoria or Investimento, start date), delete. Calm honest microcopy: items auto-created up to today only, editable/skippable, skipping creates no Drift; inviting empty state (no gamification). Mutations invalidate regole/movimenti/liquidita/patrimonio. Note: inline edit of an existing Regola is a follow-up (create + delete shipped).

## Files
**Added:** frontend/src/routes/_layout/regole.tsx
**Modified:** frontend/src/routes/_layout/settings.tsx, frontend/src/lib/api/*
