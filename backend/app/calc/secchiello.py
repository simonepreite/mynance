"""Pure derived-on-read Secchiello engine (FR-9/10/11, Stories 3.2/3.3). NO DB/IO.

A Secchiello's *Saldo* and recommended *Quota* are derived by replaying inputs
**chronologically** from the start date — no scheduler, no stored balance:

- each elapsed month credits that month's *Quota* (computed from the Saldo and
  the months-remaining as of that month) — a virtual credit that moves the
  Secchiello Saldo but never Liquidità;
- each linked *Spesa* is applied (subtracted) on its date.

The result is order-independent (by date), so a back-dated Spesa edit recomputes
correctly. A negative Saldo (under-funding) is surfaced with sign, never clamped.
"""

import math
from datetime import date

from app.calc.money import Cents, div_round

DAYS_PER_MONTH = 30.44


def _next_month(d: date) -> date:
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


def mesi_alla_scadenza(prossima_scadenza: date, ref: date) -> int:
    """``max(1, ceil((scadenza − ref) / 30.44))`` — due/overdue ⇒ 1."""
    return max(1, math.ceil((prossima_scadenza - ref).days / DAYS_PER_MONTH))


def _quota(importo_previsto_cents: Cents, saldo: Cents, mesi: int) -> Cents:
    """``max(0, (Importo previsto − Saldo) / mesi)`` in integer cents."""
    outstanding = importo_previsto_cents - saldo
    if outstanding <= 0:
        return 0
    return div_round(outstanding, mesi)


def compute_saldo_quota(
    *,
    data_inizio: date,
    importo_previsto_cents: Cents,
    prossima_scadenza: date,
    spese: list[tuple[date, Cents]],
    today: date,
) -> tuple[Cents, Cents]:
    """Return ``(saldo_cents, quota_cents)`` for the Secchiello as of ``today``.

    ``spese`` are ``(date, amount_cents)`` linked Spese; only those on/before
    ``today`` are applied. Chronological month-by-month replay (credit Quota,
    then apply that month's Spese). Negative Saldo is returned with sign.
    """
    saldo: Cents = 0
    month = data_inizio.replace(day=1)
    last = today.replace(day=1)
    while month <= last:
        nxt = _next_month(month)
        mesi = mesi_alla_scadenza(prossima_scadenza, month)
        saldo += _quota(importo_previsto_cents, saldo, mesi)
        for d, amount in spese:
            if month <= d < nxt and d <= today:
                saldo -= amount
        month = nxt

    quota = _quota(
        importo_previsto_cents, saldo, mesi_alla_scadenza(prossima_scadenza, today)
    )
    return saldo, quota
