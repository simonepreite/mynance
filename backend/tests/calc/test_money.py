"""Integer-cents money convention (Story 1.1, AC7)."""

from decimal import Decimal

import pytest

from app.calc.money import add, cents_to_euros, euros_to_cents


def test_euros_to_cents_returns_int() -> None:
    result = euros_to_cents(Decimal("12.34"))
    assert result == 1234
    assert type(result) is int


def test_half_up_rounding() -> None:
    assert euros_to_cents(Decimal("0.005")) == 1
    assert euros_to_cents(Decimal("0.004")) == 0
    assert euros_to_cents("1.005") == 101


def test_float_is_rejected() -> None:
    # Floats cannot represent decimal money exactly — must be refused.
    with pytest.raises(TypeError):
        euros_to_cents(12.34)  # type: ignore[arg-type]


def test_round_trip_is_exact_decimal() -> None:
    euros = cents_to_euros(1234)
    assert euros == Decimal("12.34")
    assert isinstance(euros, Decimal)


def test_add_keeps_integer_cents() -> None:
    total = add(1000, 250, -300)
    assert total == 950
    assert type(total) is int


def test_cents_to_euros_rejects_float() -> None:
    with pytest.raises(TypeError):
        cents_to_euros(12.34)  # type: ignore[arg-type]
