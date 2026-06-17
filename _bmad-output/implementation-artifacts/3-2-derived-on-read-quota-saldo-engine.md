---
baseline_commit: a1e10eb
---

# Story 3.2: Derived-on-read Quota & Saldo engine (FR-9, FR-11)

Status: done

## Acceptance Criteria (summary)

- **AC1 — pure module:** computation in `app/calc/secchiello.py` (no DB/framework), covered by worked-example tests in `tests/calc/`.
- **AC2 — months-to-due:** `mesi = max(1, ceil((prossima_scadenza − ref) / 30.44))`, derived from the date independently of the Periodicità label; due/overdue ⇒ `mesi = 1`.
- **AC3 — Quota:** `Quota = max(0, (Importo previsto − Saldo) / mesi)` in integer cents with centralized HALF_UP rounding; `Saldo ≥ Importo` ⇒ 0; negative Saldo raises the Quota to recover.
- **AC4 — determinism:** same inputs read twice ⇒ identical Quota/Saldo; Quota is returned read-only (client never recomputes).
- **AC5 — authZ first:** a non-owned Secchiello is rejected (404) before any computation.

## Implementation

- `compute_saldo_quota(...)` and `mesi_alla_scadenza(...)` in `app/calc/secchiello.py`; rounding centralized via the new `money.div_round` (Decimal HALF_UP). [backend/app/calc/secchiello.py, backend/app/calc/money.py]
- Wired into `SecchielloPublic.saldo_cents/quota_cents` (read-only) by the secchielli routes; the authZ choke point (`UserScopedRepository.get` → 404) runs before the engine. [backend/app/api/routes/secchielli.py]
- Tests: funding→quota 0, negative-Saldo recovery (exact cents), order-independence, future-Spese excluded, overdue⇒mesi 1; plus `div_round` HALF_UP/float-rejection. [backend/tests/calc/test_secchiello.py, backend/tests/calc/test_money.py]

### Completion Notes

_Pure, deterministic; ruff/mypy clean, pytest green. The engine is the single source of Quota/Saldo; the API exposes them read-only._

### File List

**Added:** `backend/app/calc/secchiello.py`, `backend/tests/calc/test_secchiello.py`
**Modified:** `backend/app/calc/money.py` (`div_round`), `backend/app/models.py` (`SecchielloPublic`), `backend/app/api/routes/secchielli.py`
