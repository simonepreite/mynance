---
baseline_commit: a1e10eb
---

# Story 3.3: Funding, payment & carryover lifecycle with negative Saldo surfaced (FR-10)

Status: done

## Acceptance Criteria (summary)

- **AC1 — chronological replay:** Saldo is derived by replaying from `data_inizio` — each elapsed month credits that month's Quota (virtual: moves Saldo, never Liquidità), each linked Spesa applied on its date; no scheduler/stored balance.
- **AC2 — order by date:** the month-by-month evaluation (credit, then apply that month's Spese) is deterministic and a back-dated Spesa edit recomputes correctly (order is by date, not insertion).
- **AC3 — payment decrements Saldo:** a linked Spesa (default from the Categoria, overridable per-Spesa — Story 3.1) decrements the Saldo by its actual cents; the resulting Saldo (±) is the carryover.
- **AC4 — negative surfaced:** an under-funded Secchiello shows its negative Saldo with sign (warm-amber in the UI, Story 3.4), never clamped in the bucket's own view.
- **AC5 — edit/delete recompute:** editing/deleting the linked Spesa recomputes Saldo/carryover/Quota consistently, no Movimento lost.

## Implementation

- The replay (AC1/AC2/AC4) is implemented in the pure `compute_saldo_quota` engine (Story 3.2): month loop crediting Quota then subtracting that month's linked Spese; negative Saldo returned with sign. [backend/app/calc/secchiello.py]
- The linked-Spesa decrement (AC3) flows from the Movimento `secchiello_id` link (Story 3.1); editing/deleting a Spesa (Story 2.5 endpoints) changes the inputs, so the next read recomputes (AC5). Tested via the API (`saldo1 == saldo0 − spesa`). [backend/tests/api/test_secchielli.py, backend/tests/calc/test_secchiello.py]

### Completion Notes

_The derived computation (replay, virtual credit, negative Saldo, Spesa decrement, back-dated correctness) is complete and tested._

_**Deferred / simplified:** the automatic cycle advance on payment — updating `importo_previsto` to the actual paid amount and advancing `prossima_scadenza` by the Periodicità when a payment Spesa is logged — is not yet automatic. For now the Utente advances the cycle via a `PATCH /secchielli/{id}` edit (the engine already carries the Saldo over and the Quota reflects it). The auto-advance-on-payment is a focused follow-up (it needs a rule for which Spesa counts as "the payment") tracked for a later refinement; it does not affect the honesty of the derived Saldo/Quota._

### File List

(Shared with 3.1/3.2.) **Modified:** `backend/app/calc/secchiello.py`, `backend/app/api/routes/movimenti.py`, `backend/tests/api/test_secchielli.py`
