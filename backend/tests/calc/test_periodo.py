"""Pure period-boundary math (Stories 2.8/2.9). No DB (see tests/calc/conftest.py)."""

from datetime import date

import pytest

from app.calc.periodo import month_anchors_back, period_bounds


def test_day_bounds() -> None:
    assert period_bounds("day", date(2026, 6, 17)) == (
        date(2026, 6, 17),
        date(2026, 6, 18),
    )


def test_week_starts_monday() -> None:
    # 2026-06-17 is a Wednesday → week is Mon 15 .. next Mon 22.
    assert period_bounds("week", date(2026, 6, 17)) == (
        date(2026, 6, 15),
        date(2026, 6, 22),
    )


def test_month_bounds_and_december_rollover() -> None:
    assert period_bounds("month", date(2026, 6, 17)) == (
        date(2026, 6, 1),
        date(2026, 7, 1),
    )
    assert period_bounds("month", date(2026, 12, 31)) == (
        date(2026, 12, 1),
        date(2027, 1, 1),
    )


def test_year_bounds() -> None:
    assert period_bounds("year", date(2026, 6, 17)) == (
        date(2026, 1, 1),
        date(2027, 1, 1),
    )


def test_invalid_period_raises() -> None:
    with pytest.raises(ValueError):
        period_bounds("decade", date(2026, 6, 17))


def test_month_anchors_back_oldest_to_newest_crossing_year() -> None:
    anchors = month_anchors_back(date(2026, 2, 10), 4)
    assert anchors == [
        date(2025, 11, 1),
        date(2025, 12, 1),
        date(2026, 1, 1),
        date(2026, 2, 1),
    ]


def test_month_anchors_back_zero() -> None:
    assert month_anchors_back(date(2026, 6, 1), 0) == []
