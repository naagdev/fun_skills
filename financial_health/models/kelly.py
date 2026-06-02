"""
Kelly Criterion for position sizing.

  f* = (b·p − q) / b   where b = win/loss ratio, p = P(win), q = 1−p

We use half-Kelly (f*/2) as standard practice — full Kelly is theoretically
optimal but has severe drawdown in practice.

Inputs:
  - current_price, target_price (analyst consensus)
  - expected_downside: estimated max loss in bear case (e.g. 0.35 = 35%)
  - win_probability: estimated P(stock reaches target) over the horizon
  - portfolio_size: total capital to allocate across all positions

Outputs per stock:
  - full Kelly %
  - half Kelly %
  - recommended dollar allocation
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class KellyResult:
    ticker: str
    current_price: float
    target_price: float
    expected_upside: float      # fractional
    expected_downside: float    # fractional (positive = loss magnitude)
    win_probability: float
    b_ratio: float              # win / loss ratio
    full_kelly_pct: float
    half_kelly_pct: float
    dollar_allocation: float    # based on half-Kelly and portfolio_size
    portfolio_size: float


def run_kelly(
    ticker: str,
    current_price: float,
    target_price: float,
    expected_downside: float,
    win_probability: float,
    portfolio_size: float = 5000.0,
) -> KellyResult:
    upside = (target_price - current_price) / current_price
    b = upside / expected_downside          # win-to-loss ratio
    p = win_probability
    q = 1.0 - p

    full_kelly = (b * p - q) / b
    full_kelly = max(0.0, full_kelly)       # never short via Kelly
    half_kelly = full_kelly / 2.0

    return KellyResult(
        ticker=ticker,
        current_price=current_price,
        target_price=target_price,
        expected_upside=round(upside, 4),
        expected_downside=round(expected_downside, 4),
        win_probability=win_probability,
        b_ratio=round(b, 3),
        full_kelly_pct=round(full_kelly * 100, 1),
        half_kelly_pct=round(half_kelly * 100, 1),
        dollar_allocation=round(portfolio_size * half_kelly, 2),
        portfolio_size=portfolio_size,
    )
