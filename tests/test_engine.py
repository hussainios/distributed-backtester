from datetime import date

import pytest

from backtester.engine import PriceBar, run_moving_average_crossover


def test_moving_average_strategy_returns_metrics() -> None:
    prices = [PriceBar(date(2024, 1, day), float(day)) for day in range(1, 11)]

    result = run_moving_average_crossover(
        prices,
        initial_capital=1000,
        commission_bps=1,
        slippage_bps=2,
        fast_window=2,
        slow_window=3,
    )

    assert result["final_equity"] > 1000
    assert result["data_points"] == 10


def test_strategy_rejects_invalid_windows() -> None:
    with pytest.raises(ValueError, match="fast_window"):
        run_moving_average_crossover(
            [PriceBar(date(2024, 1, day), float(day)) for day in range(1, 11)],
            initial_capital=1000,
            commission_bps=1,
            slippage_bps=2,
            fast_window=3,
            slow_window=3,
        )

