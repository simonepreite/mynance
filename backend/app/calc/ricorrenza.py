"""Pure recurrence-date math for Regole ricorrenti (Epic 6, FR-8). NO DB/IO.

Computes the occurrence dates a Regola owes from its ``start_date`` up to ``today``
only (never future-dated). Day-of-period is clamped to the last valid day of each
period (e.g. day 31 in February → 28/29). Deterministic: same inputs → same dates.
"""

import calendar
from datetime import date

_MAX_OCCORRENZE = 1200  # safety bound (~100 years monthly)


def _clamp_day(year: int, month: int, day_of_period: int) -> date:
    last = calendar.monthrange(year, month)[1]
    return date(year, month, min(day_of_period, last))


def _step_month(year: int, month: int, intervallo_mesi: int) -> tuple[int, int]:
    idx = (month - 1) + intervallo_mesi
    return year + idx // 12, idx % 12 + 1


def occorrenze_due(
    *,
    start_date: date,
    intervallo_mesi: int,
    day_of_period: int,
    today: date,
) -> list[date]:
    """Occurrence dates from ``start_date`` to ``today`` inclusive (≤ today only)."""
    if intervallo_mesi < 1:
        raise ValueError("intervallo_mesi must be ≥ 1")
    occorrenze: list[date] = []
    year, month = start_date.year, start_date.month
    for _ in range(_MAX_OCCORRENZE):
        d = _clamp_day(year, month, day_of_period)
        if d > today:
            break
        if d >= start_date:
            occorrenze.append(d)
        year, month = _step_month(year, month, intervallo_mesi)
    return occorrenze
