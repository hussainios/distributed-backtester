from dataclasses import dataclass
from datetime import date, timedelta
from hashlib import sha256
from math import sqrt
from typing import Any


@dataclass(frozen=True)
class PriceBar:
    date: date
    close: float


def load_demo_prices(instrument: str, start_date: date, end_date: date) -> list[PriceBar]:
    seed = int.from_bytes(sha256(instrument.encode()).digest()[:4], "big")
    price = float(80 + seed % 120)
    bars: list[PriceBar] = []
    current_date = start_date
    day_number = 0
    while current_date <= end_date:
        if current_date.weekday() < 5:
            movement = (((seed + day_number * 17) % 200) - 100) / 10_000
            price = max(1, price * (1 + movement))
            bars.append(PriceBar(current_date, round(price, 4)))
            day_number += 1
        current_date += timedelta(days=1)
    return bars


def run_moving_average_crossover(
    prices: list[PriceBar],
    *,
    initial_capital: float,
    commission_bps: float,
    slippage_bps: float,
    fast_window: int,
    slow_window: int,
) -> dict[str, Any]:
    if fast_window <= 0 or slow_window <= 0 or fast_window >= slow_window:
        raise ValueError("fast_window must be positive and smaller than slow_window")
    if len(prices) < slow_window + 1:
        raise ValueError("date range does not contain enough trading days for the strategy")

    equity = initial_capital
    previous_signal = 0
    equity_curve = [initial_capital]
    trades: list[dict[str, Any]] = []
    total_cost_rate = (commission_bps + slippage_bps) / 10_000

    for index in range(slow_window, len(prices)):
        fast_prices = prices[index - fast_window + 1 : index + 1]
        slow_prices = prices[index - slow_window + 1 : index + 1]
        fast_average = sum(bar.close for bar in fast_prices) / fast_window
        slow_average = sum(bar.close for bar in slow_prices) / slow_window
        signal = 1 if fast_average > slow_average else 0
        previous_price = prices[index - 1].close
        current_price = prices[index].close

        if previous_signal == 1:
            equity *= current_price / previous_price
        if signal != previous_signal:
            equity *= 1 - total_cost_rate
            trades.append(
                {
                    "date": prices[index].date.isoformat(),
                    "side": "buy" if signal else "sell",
                    "price": current_price,
                }
            )
        previous_signal = signal
        equity_curve.append(equity)

    returns = [
        equity_curve[index] / equity_curve[index - 1] - 1
        for index in range(1, len(equity_curve))
    ]
    average_return = sum(returns) / len(returns)
    variance = sum((value - average_return) ** 2 for value in returns) / len(returns)
    volatility = sqrt(variance)
    peak = equity_curve[0]
    max_drawdown = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        max_drawdown = min(max_drawdown, value / peak - 1)

    return {
        "final_equity": round(equity, 2),
        "total_return": round(equity / initial_capital - 1, 6),
        "max_drawdown": round(max_drawdown, 6),
        "daily_sharpe": round(average_return / volatility * sqrt(252), 6) if volatility else 0.0,
        "trade_count": len(trades),
        "trades": trades,
        "data_points": len(prices),
    }


def run_backtest(
    *,
    strategy: str,
    parameters: dict[str, Any],
    instrument: str,
    start_date: date,
    end_date: date,
    initial_capital: float,
    commission_bps: float,
    slippage_bps: float,
) -> dict[str, Any]:
    if strategy != "moving_average_crossover":
        raise ValueError(f"unknown strategy: {strategy}")

    prices = load_demo_prices(instrument, start_date, end_date)
    return run_moving_average_crossover(
        prices,
        initial_capital=initial_capital,
        commission_bps=commission_bps,
        slippage_bps=slippage_bps,
        fast_window=int(parameters.get("fast_window", 20)),
        slow_window=int(parameters.get("slow_window", 50)),
    )
