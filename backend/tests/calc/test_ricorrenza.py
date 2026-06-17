"""Pure recurrence-date math (Epic 6). No DB (calc conftest)."""

from datetime import date

from app.calc.ricorrenza import occorrenze_due


def test_monthly_up_to_today_only() -> None:
    occ = occorrenze_due(
        start_date=date(2026, 3, 1),
        intervallo_mesi=1,
        day_of_period=1,
        today=date(2026, 6, 17),
    )
    assert occ == [
        date(2026, 3, 1),
        date(2026, 4, 1),
        date(2026, 5, 1),
        date(2026, 6, 1),
    ]


def test_no_future_occurrences() -> None:
    occ = occorrenze_due(
        start_date=date(2026, 6, 1),
        intervallo_mesi=1,
        day_of_period=20,
        today=date(2026, 6, 17),
    )
    # day 20 of June is after today (17) → not yet due.
    assert occ == []


def test_day_31_clamps_to_short_months() -> None:
    occ = occorrenze_due(
        start_date=date(2026, 1, 31),
        intervallo_mesi=1,
        day_of_period=31,
        today=date(2026, 3, 31),
    )
    assert occ == [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)]


def test_custom_interval_every_two_months() -> None:
    occ = occorrenze_due(
        start_date=date(2026, 1, 15),
        intervallo_mesi=2,
        day_of_period=15,
        today=date(2026, 6, 17),
    )
    assert occ == [date(2026, 1, 15), date(2026, 3, 15), date(2026, 5, 15)]


def test_first_occurrence_respects_start_date() -> None:
    # start mid-month after the day-of-period → first due is next period.
    occ = occorrenze_due(
        start_date=date(2026, 1, 20),
        intervallo_mesi=1,
        day_of_period=10,
        today=date(2026, 3, 31),
    )
    assert occ == [date(2026, 2, 10), date(2026, 3, 10)]
