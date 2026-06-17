"""Pure period-boundary math (Stories 2.8/2.9, UX-DR3). NO DB/IO.

Periods are half-open calendar ranges ``[start, end)`` over plain dates.
``Movimento.data`` is a date (no time), so boundaries are timezone-free calendar
dates — the Europe/Rome calendar with no instant-shifting. Week starts Monday.
"""

from datetime import date, timedelta

VALID_PERIODS = ("day", "week", "month", "year")


def _first_of_next_month(d: date) -> date:
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


def period_bounds(period: str, anchor: date) -> tuple[date, date]:
    """Half-open ``[start, end)`` for the period containing ``anchor``."""
    if period == "day":
        return anchor, anchor + timedelta(days=1)
    if period == "week":
        start = anchor - timedelta(days=anchor.weekday())  # Monday
        return start, start + timedelta(days=7)
    if period == "month":
        start = anchor.replace(day=1)
        return start, _first_of_next_month(start)
    if period == "year":
        return date(anchor.year, 1, 1), date(anchor.year + 1, 1, 1)
    raise ValueError(f"unknown period: {period!r}")


def month_anchors_back(anchor: date, count: int) -> list[date]:
    """First-of-month dates for ``count`` months up to anchor's month (oldest→newest)."""
    if count < 1:
        return []
    months: list[date] = []
    cursor = anchor.replace(day=1)
    for _ in range(count):
        months.append(cursor)
        # step back one month
        cursor = (
            date(cursor.year - 1, 12, 1)
            if cursor.month == 1
            else date(cursor.year, cursor.month - 1, 1)
        )
    return list(reversed(months))
