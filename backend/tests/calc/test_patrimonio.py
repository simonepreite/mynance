"""Pure Patrimonio math: linear Svalutazione + total (Story 5.3/5.4). No DB."""

from datetime import date

from app.calc.patrimonio import patrimonio_totale, valore_bene_mobile


def test_no_time_elapsed_is_full_price() -> None:
    v = valore_bene_mobile(
        prezzo_cents=100000,
        svalutazione_percentuale=20.0,
        data_acquisto=date(2026, 6, 17),
        today=date(2026, 6, 17),
    )
    assert v == 100000


def test_zero_rate_keeps_full_price() -> None:
    v = valore_bene_mobile(
        prezzo_cents=100000,
        svalutazione_percentuale=0.0,
        data_acquisto=date(2020, 1, 1),
        today=date(2026, 6, 17),
    )
    assert v == 100000


def test_fully_depreciated_floors_at_zero() -> None:
    # s=50%/yr over ~3 years → s·anni ≥ 1 → 0, never negative.
    v = valore_bene_mobile(
        prezzo_cents=100000,
        svalutazione_percentuale=50.0,
        data_acquisto=date(2023, 1, 1),
        today=date(2026, 6, 17),
    )
    assert v == 0


def test_partial_depreciation_between_zero_and_price() -> None:
    v = valore_bene_mobile(
        prezzo_cents=100000,
        svalutazione_percentuale=15.0,
        data_acquisto=date(2025, 6, 17),
        today=date(2026, 6, 17),
    )
    assert 0 < v < 100000  # ~1 year at 15% → ~85000


def test_totale_sums_with_signed_liquidita() -> None:
    assert (
        patrimonio_totale(
            liquidita_cents=-5000,
            capitale_versato_cents=30000,
            beni_immobili_cents=20000000,
            beni_mobili_cents=80000,
        )
        == -5000 + 30000 + 20000000 + 80000
    )
