"""Pure allocation + cuscinetto math (Stories 3.5/3.6). No DB (calc conftest)."""

from app.calc.allocazione import (
    cuscinetto,
    liquidita_allocata,
    risparmio_libero,
    spesa_media_mensile,
)


def test_allocata_sums_only_positive_saldi() -> None:
    # A negative Saldo contributes 0 to the allocation total.
    assert liquidita_allocata([30000, -5000, 12000]) == 42000
    assert liquidita_allocata([]) == 0
    assert liquidita_allocata([-100, -200]) == 0


def test_risparmio_libero_can_be_negative() -> None:
    assert risparmio_libero(100000, 42000) == 58000
    assert risparmio_libero(10000, 42000) == -32000


def test_spesa_media_mensile_mean_and_empty() -> None:
    assert spesa_media_mensile([100000, 100000]) == 100000
    assert spesa_media_mensile([100000, 50000, 30000]) == 60000
    assert spesa_media_mensile([]) == 0
    # HALF_UP rounding to whole cents.
    assert spesa_media_mensile([100, 100, 101]) == 100  # 100.33 → 100


def test_cuscinetto_is_n_times_media() -> None:
    assert cuscinetto(100000, 6) == 600000
    assert cuscinetto(0, 6) == 0
    assert cuscinetto(50000, 0) == 0
