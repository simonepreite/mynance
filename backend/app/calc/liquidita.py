"""Pure derived-on-read Liquidità engine (AR-Calc, FR-13, NFR-1). NO DB/IO.

    Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato

All arithmetic is in integer cents (never float). An unset baseline is treated
as 0 cents. Negative results are returned with sign — never clamped (honesty
principle). The function is pure and order-independent, so it is deterministic
and reproducible (NFR-1) and unit-testable in isolation.
"""

from collections.abc import Iterable

from app.calc.money import Cents, add


def compute_liquidita(
    *,
    iniziale_cents: Cents | None,
    entrate_cents: Iterable[Cents] = (),
    spese_cents: Iterable[Cents] = (),
    capitale_versato_cents: Iterable[Cents] = (),
) -> Cents:
    """Derive current Liquidità in integer cents from stored inputs.

    ``iniziale_cents`` may be ``None`` (unset → treated as 0). The Capitale
    versato set may be empty (no Investimenti yet); an empty set sums to 0.
    """
    base: Cents = iniziale_cents if iniziale_cents is not None else 0
    return base + add(*entrate_cents) - add(*spese_cents) - add(*capitale_versato_cents)
