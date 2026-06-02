"""
2-stage Discounted Cash Flow model with sensitivity table.

Stage 1: high-growth years 1-5
Stage 2: transition years 6-10
Terminal: Gordon Growth Model perpetuity
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DCFResult:
    ticker: str
    current_price: float
    fair_value: float
    upside_pct: float
    fcf_used: float          # B USD
    wacc: float
    stage1_growth: float
    stage2_growth: float
    terminal_growth: float
    # sensitivity[(wacc_pct, g1_pct)] = fair_value
    sensitivity: dict = field(default_factory=dict)


def _single_dcf(
    fcf: float,
    shares: float,
    net_debt: float,
    g1: float,
    g2: float,
    wacc: float,
    tg: float = 0.03,
    n1: int = 5,
    n2: int = 5,
) -> float:
    pv = 0.0
    cf = fcf
    for t in range(1, n1 + 1):
        cf *= (1 + g1)
        pv += cf / (1 + wacc) ** t
    for t in range(n1 + 1, n1 + n2 + 1):
        cf *= (1 + g2)
        pv += cf / (1 + wacc) ** t
    tv = cf * (1 + tg) / (wacc - tg)
    pv += tv / (1 + wacc) ** (n1 + n2)
    equity = pv - net_debt
    return equity / shares


def run_dcf(
    ticker: str,
    fcf: float,
    shares: float,
    net_debt: float,
    current_price: float,
    stage1_growth: float = 0.25,
    stage2_growth: float = 0.12,
    terminal_growth: float = 0.03,
    wacc: float = 0.10,
) -> DCFResult:
    base_fv = _single_dcf(fcf, shares, net_debt, stage1_growth, stage2_growth, wacc, terminal_growth)

    wacc_range   = [0.09, 0.10, 0.11, 0.12, 0.13]
    growth_range = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    sensitivity  = {}
    for w in wacc_range:
        for g in growth_range:
            sensitivity[(round(w, 2), round(g, 2))] = _single_dcf(
                fcf, shares, net_debt, g, stage2_growth, w, terminal_growth
            )

    return DCFResult(
        ticker=ticker,
        current_price=current_price,
        fair_value=round(base_fv, 2),
        upside_pct=round((base_fv - current_price) / current_price * 100, 1),
        fcf_used=fcf,
        wacc=wacc,
        stage1_growth=stage1_growth,
        stage2_growth=stage2_growth,
        terminal_growth=terminal_growth,
        sensitivity=sensitivity,
    )
