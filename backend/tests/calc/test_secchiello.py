"""Pure Secchiello Quota/Saldo engine (Stories 3.2/3.3). No DB (calc conftest)."""

from datetime import date

from app.calc.secchiello import compute_saldo_quota, mesi_alla_scadenza


def test_single_month_fully_funds_then_quota_zero() -> None:
    # Due next month: month 1 credits the whole importo; once funded, quota = 0.
    saldo, quota = compute_saldo_quota(
        data_inizio=date(2026, 6, 1),
        importo_previsto_cents=10000,
        prossima_scadenza=date(2026, 7, 1),
        spese=[],
        today=date(2026, 6, 1),
    )
    assert saldo == 10000
    assert quota == 0


def test_negative_saldo_surfaced_and_quota_recovers() -> None:
    # 1429 credited (10000/7, HALF_UP), then a 30000 Spesa → Saldo −28571 (never
    # clamped); Quota rises to recover the shortfall over the months remaining.
    saldo, quota = compute_saldo_quota(
        data_inizio=date(2026, 6, 1),
        importo_previsto_cents=10000,
        prossima_scadenza=date(2026, 12, 1),
        spese=[(date(2026, 6, 1), 30000)],
        today=date(2026, 6, 1),
    )
    assert saldo == -28571
    assert quota == 5510


def test_spese_order_independent() -> None:
    common = {
        "data_inizio": date(2026, 1, 1),
        "importo_previsto_cents": 120000,
        "prossima_scadenza": date(2026, 12, 1),
        "today": date(2026, 6, 15),
    }
    a = compute_saldo_quota(
        spese=[(date(2026, 3, 10), 5000), (date(2026, 5, 2), 8000)], **common
    )
    b = compute_saldo_quota(
        spese=[(date(2026, 5, 2), 8000), (date(2026, 3, 10), 5000)], **common
    )
    assert a == b


def test_future_spese_not_applied() -> None:
    common = {
        "data_inizio": date(2026, 6, 1),
        "importo_previsto_cents": 10000,
        "prossima_scadenza": date(2026, 12, 1),
        "today": date(2026, 6, 15),
    }
    with_future = compute_saldo_quota(spese=[(date(2026, 12, 1), 5000)], **common)
    without = compute_saldo_quota(spese=[], **common)
    assert with_future == without


def test_mesi_alla_scadenza_overdue_is_one() -> None:
    assert mesi_alla_scadenza(date(2026, 5, 1), date(2026, 6, 1)) == 1
    assert mesi_alla_scadenza(date(2026, 6, 1), date(2026, 6, 1)) == 1
