"""
Monte Carlo DCF — runs N simulations sampling growth rates and WACC from
normal distributions to produce a probability distribution of fair value.
"""

from __future__ import annotations

import random
import math
from dataclasses import dataclass

from .dcf import _single_dcf


@dataclass
class MonteCarloResult:
    ticker: str
    current_price: float
    n_simulations: int
    mean: float
    median: float
    p10: float      # 10th percentile (bear)
    p25: float
    p75: float
    p90: float      # 90th percentile (bull)
    prob_undervalued: float   # fraction of sims where fair_value > current_price
    prob_20pct_upside: float
    prob_loss: float          # fair_value < current * 0.9


def _percentile(data: list[float], p: float) -> float:
    data = sorted(data)
    k = (len(data) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(data) - 1)
    return data[lo] + (data[hi] - data[lo]) * (k - lo)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def run_monte_carlo(
    ticker: str,
    fcf: float,
    shares: float,
    net_debt: float,
    current_price: float,
    base_g1: float = 0.25,
    base_g2: float = 0.12,
    base_wacc: float = 0.10,
    terminal_growth: float = 0.03,
    n: int = 10_000,
    seed: int = 42,
) -> MonteCarloResult:
    rng = random.Random(seed)

    def _gauss(mu, sigma):
        # Box-Muller via Python random
        return rng.gauss(mu, sigma)

    results = []
    for _ in range(n):
        g1   = _clamp(_gauss(base_g1,   0.10), 0.00, 0.90)
        g2   = _clamp(_gauss(base_g2,   0.06), 0.00, 0.50)
        wacc = _clamp(_gauss(base_wacc, 0.015), 0.06, 0.20)
        if wacc <= terminal_growth:
            wacc = terminal_growth + 0.01
        fv = _single_dcf(fcf, shares, net_debt, g1, g2, wacc, terminal_growth)
        results.append(fv)

    prob_under = sum(1 for v in results if v > current_price) / n
    prob_20    = sum(1 for v in results if v > current_price * 1.20) / n
    prob_loss  = sum(1 for v in results if v < current_price * 0.90) / n

    return MonteCarloResult(
        ticker=ticker,
        current_price=current_price,
        n_simulations=n,
        mean=round(sum(results) / n, 2),
        median=round(_percentile(results, 50), 2),
        p10=round(_percentile(results, 10), 2),
        p25=round(_percentile(results, 25), 2),
        p75=round(_percentile(results, 75), 2),
        p90=round(_percentile(results, 90), 2),
        prob_undervalued=round(prob_under * 100, 1),
        prob_20pct_upside=round(prob_20 * 100, 1),
        prob_loss=round(prob_loss * 100, 1),
    )
