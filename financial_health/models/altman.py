"""
Altman Z''-Score (modified for non-manufacturers / tech companies).

Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4

X1 = Working Capital / Total Assets        (liquidity)
X2 = Retained Earnings / Total Assets      (cumulative profitability)
X3 = EBIT / Total Assets                   (operating efficiency)
X4 = Market Cap / Total Liabilities        (solvency buffer)

Zones:
  Z'' > 2.60  →  Safe
  1.10–2.60   →  Grey (watch)
  Z'' < 1.10  →  Distress
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AltmanComponent:
    name: str
    coefficient: float
    ratio: float
    contribution: float


@dataclass
class AltmanResult:
    ticker: str
    z_score: float
    zone: str        # "Safe" | "Grey" | "Distress"
    components: list[AltmanComponent] = field(default_factory=list)


def run_altman(
    ticker: str,
    working_capital: float,    # B
    total_assets: float,       # B
    retained_earnings: float,  # B  (may be negative for acquisition-heavy companies)
    ebit: float,               # B
    market_cap: float,         # B
    total_liabilities: float,  # B
) -> AltmanResult:

    x1 = working_capital   / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit              / total_assets
    x4 = market_cap        / total_liabilities

    coeffs = [
        ("Working Capital / Total Assets",       6.56, x1),
        ("Retained Earnings / Total Assets",     3.26, x2),
        ("EBIT / Total Assets",                  6.72, x3),
        ("Market Cap / Total Liabilities",       1.05, x4),
    ]

    components = [
        AltmanComponent(name=n, coefficient=c, ratio=round(r, 4),
                        contribution=round(c * r, 4))
        for n, c, r in coeffs
    ]

    z = sum(comp.contribution for comp in components)

    if z > 2.60:
        zone = "Safe"
    elif z >= 1.10:
        zone = "Grey"
    else:
        zone = "Distress"

    return AltmanResult(ticker=ticker, z_score=round(z, 3), zone=zone, components=components)
