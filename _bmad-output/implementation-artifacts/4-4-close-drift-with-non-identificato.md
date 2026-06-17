---
baseline_commit: badb988
---

# Story 4.4: Close the Drift with a "non identificato" Movimento (FR-18)

Status: done

## Summary
- Confirm with esito=chiusa and drift≠0 creates a single plug Movimento for |drift| on the matching system "non identificato" Categoria: Spesa when R<C, Entrata when R>C (sign self-selects the type); amount = |R−C| exactly.
- After the plug, derived Liquidità equals the entered real figure (tested: GET /liquidita == reale). The plug Movimento is reportable like any other (appears in Home breakdown / Statistiche pie / Spesa media mensile via its "non identificato" Categoria).
- Drift = 0 → no plug; Riconciliazione still recorded, timer resets.
- Frontend "Chiudi lo scostamento" action; non-optimistic mutation (warm error + retry on failure, no partial commit).

## Files
**Modified:** backend/app/api/routes/riconciliazione.py, frontend/src/routes/_layout/riconciliazione.tsx
