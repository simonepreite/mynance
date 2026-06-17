"""Pure Patrimonio math (Epic 5, FR-21/FR-22). NO DB/IO.

Beni mobili lose value by straight-line Svalutazione, floored at 0:

    Valore = max(0, prezzo × (1 − s × anni_trascorsi))

where ``s`` is the annual rate (fraction) and ``anni_trascorsi`` is the
fractional time in years from purchase to today. Money stays integer cents with
centralized rounding.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from app.calc.money import Cents

DAYS_PER_YEAR = Decimal("365.25")


def valore_bene_mobile(
    *,
    prezzo_cents: Cents,
    svalutazione_percentuale: float,
    data_acquisto: date,
    today: date,
) -> Cents:
    """Current depreciated value in integer cents, floored at 0."""
    giorni = max(0, (today - data_acquisto).days)
    anni = Decimal(giorni) / DAYS_PER_YEAR
    s = Decimal(str(svalutazione_percentuale)) / Decimal(100)
    fattore = Decimal(1) - s * anni
    if fattore <= 0:
        return 0
    valore = (Decimal(prezzo_cents) * fattore).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return max(0, int(valore))


def patrimonio_totale(
    *,
    liquidita_cents: Cents,
    capitale_versato_cents: Cents,
    beni_immobili_cents: Cents,
    beni_mobili_cents: Cents,
) -> Cents:
    """Total net worth = Liquidità + Capitale versato + beni immobili + beni mobili.

    Liquidità may be negative (honesty): it is summed with sign, never clamped.
    """
    return (
        liquidita_cents
        + capitale_versato_cents
        + beni_immobili_cents
        + beni_mobili_cents
    )
