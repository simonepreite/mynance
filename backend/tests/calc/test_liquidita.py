"""Pure Liquidità engine — worked examples + determinism (Story 2.3, FR-13/NFR-1).

These tests are pure (no DB; see tests/calc/conftest.py).
"""

import pytest

from app.calc.liquidita import compute_liquidita


def test_worked_reference_example() -> None:
    # iniziale 100000; entrate 250000 + 50000; spese 45000 + 1299 + 90000.
    # 100000 + 300000 − 136299 = 263701 (hand-computed).
    result = compute_liquidita(
        iniziale_cents=100000,
        entrate_cents=[250000, 50000],
        spese_cents=[45000, 1299, 90000],
    )
    assert result == 263701
    assert type(result) is int


def test_negative_result_is_surfaced_never_clamped() -> None:
    # Spese exceed iniziale + entrate → negative Liquidità, returned with sign.
    assert compute_liquidita(iniziale_cents=0, spese_cents=[5000]) == -5000
    assert (
        compute_liquidita(
            iniziale_cents=10000, entrate_cents=[2000], spese_cents=[50000]
        )
        == -38000
    )


def test_unset_baseline_treated_as_zero() -> None:
    assert compute_liquidita(iniziale_cents=None) == 0
    assert compute_liquidita(iniziale_cents=None, entrate_cents=[1000]) == 1000
    assert compute_liquidita(iniziale_cents=None, spese_cents=[1, 2, 3]) == -6


def test_empty_collections_sum_to_zero() -> None:
    assert compute_liquidita(iniziale_cents=42) == 42


def test_capitale_versato_is_subtracted() -> None:
    # Capitale versato reduces Liquidità (cash moved into Investimenti).
    assert (
        compute_liquidita(
            iniziale_cents=100000,
            entrate_cents=[50000],
            capitale_versato_cents=[30000],
        )
        == 120000
    )


def test_order_independent_and_deterministic() -> None:
    a = compute_liquidita(
        iniziale_cents=100000,
        entrate_cents=[250000, 50000],
        spese_cents=[45000, 1299, 90000],
    )
    b = compute_liquidita(
        iniziale_cents=100000,
        entrate_cents=[50000, 250000],
        spese_cents=[90000, 45000, 1299],
    )
    assert a == b == 263701


def test_rejects_float_inputs_no_drift() -> None:
    # The engine must never accept float money (delegates the guard to money.add).
    with pytest.raises(TypeError):
        compute_liquidita(iniziale_cents=0, spese_cents=[10.0])  # type: ignore[list-item]
