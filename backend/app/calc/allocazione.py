"""Pure allocation + safety-buffer math (FR-14/FR-15, Stories 3.5/3.6). NO DB/IO.

- *Liquidità allocata* = Σ max(0, Saldo) over Secchielli (a negative Saldo
  contributes 0 to the allocation total; the bucket still shows its own
  negative Saldo per Story 3.3).
- *Risparmio libero* = *Liquidità* − *Liquidità allocata*.
- *Spesa media mensile* = mean of Spese over the available complete months.
- *Cuscinetto di sicurezza* = N × *Spesa media mensile*.

All values are integer cents.
"""

from app.calc.money import Cents, div_round


def liquidita_allocata(saldi_cents: list[Cents]) -> Cents:
    return sum(s for s in saldi_cents if s > 0)


def risparmio_libero(liquidita_cents: Cents, allocata_cents: Cents) -> Cents:
    # May be negative (honesty): more is committed/spent than is on hand.
    return liquidita_cents - allocata_cents


def spesa_media_mensile(monthly_totals_cents: list[Cents]) -> Cents:
    """Mean of the provided complete-month Spese totals (0 when none)."""
    if not monthly_totals_cents:
        return 0
    return div_round(sum(monthly_totals_cents), len(monthly_totals_cents))


def cuscinetto(media_mensile_cents: Cents, mesi: int) -> Cents:
    if mesi < 0:
        raise ValueError("mesi must be ≥ 0")
    return media_mensile_cents * mesi
