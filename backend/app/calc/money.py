"""Integer-cents money helpers — the canonical home for the cents convention.

All money in mynance is an integer number of **cents** (minor units), stored on
``BIGINT *_cents`` columns. Never a float, never a localized string in the DB or
API. Display formatting (``€ 1.234,56``) happens only at the frontend layer
(``frontend/src/lib/format.ts``).

This module is intentionally tiny: it anchors the convention so the first real
money field (Epic 2) is correct by construction. The full derived-on-read
calculation engine lands in Epic 2.
"""

from decimal import ROUND_HALF_UP, Decimal

# A money amount in integer minor units (cents). Alias for documentation.
Cents = int


def euros_to_cents(euros: Decimal | int | str) -> Cents:
    """Convert a euro amount to integer cents (canonical HALF_UP rounding).

    Accepts ``Decimal``/``int``/``str`` only — **never** ``float`` (binary
    floats cannot represent decimal money exactly).
    """
    if isinstance(euros, float):
        raise TypeError("money must be Decimal/int/str, never float")
    amount = Decimal(euros)
    cents = (amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)


def cents_to_euros(cents: Cents) -> Decimal:
    """Exact euro ``Decimal`` from integer cents (for computation, not display)."""
    if not isinstance(cents, int) or isinstance(cents, bool):
        raise TypeError("cents must be an int")
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


def add(*amounts: Cents) -> Cents:
    """Sum integer-cents amounts; the result is always integer cents."""
    for a in amounts:
        if not isinstance(a, int) or isinstance(a, bool):
            raise TypeError("amounts must be int cents")
    return sum(amounts)


def div_round(cents: Cents, divisor: int) -> Cents:
    """Divide integer cents by a positive integer, HALF_UP, returning int cents.

    Centralized money rounding (e.g. a Quota = outstanding / months); never float.
    """
    if not isinstance(cents, int) or isinstance(cents, bool):
        raise TypeError("cents must be an int")
    if divisor <= 0:
        raise ValueError("divisor must be a positive integer")
    return int(
        (Decimal(cents) / Decimal(divisor)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )
