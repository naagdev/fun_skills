"""
Piotroski F-Score (0–9).

9 binary signals across three pillars:
  Profitability  (4 signals)
  Leverage       (3 signals)
  Efficiency     (2 signals)

Score 7-9 = Strong, 4-6 = Neutral, 0-3 = Weak
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Signal:
    name: str
    passed: bool
    value: str        # human-readable value shown in report
    pillar: str


@dataclass
class PiotroskiResult:
    ticker: str
    score: int
    grade: str
    signals: list[Signal] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def run_piotroski(
    ticker: str,
    # Profitability
    roa: float,                      # current ROA
    roa_prior: float,                # prior year ROA
    ocf: float,                      # operating cash flow (B)
    total_assets: float,             # total assets (B)
    # Leverage & Liquidity
    debt_to_equity: float,           # current D/E
    debt_to_equity_prior: float,     # prior year D/E
    current_ratio: float,            # current ratio
    current_ratio_prior: float,
    shares: float,                   # current shares outstanding (M)
    shares_prior: float,             # prior year shares outstanding (M)
    # Operating Efficiency
    gross_margin: float,             # current gross margin (0–1)
    gross_margin_prior: float,
    asset_turnover: float,           # revenue / total assets
    asset_turnover_prior: float,
    notes: list[str] | None = None,
) -> PiotroskiResult:

    sigs: list[Signal] = []

    def s(name, passed, value, pillar):
        sigs.append(Signal(name=name, passed=passed, value=value, pillar=pillar))

    # ── Profitability ─────────────────────────────────────────────────────────
    s("ROA positive",
      roa > 0,
      f"{roa*100:.1f}%",
      "Profitability")

    s("Operating cash flow positive",
      ocf > 0,
      f"${ocf/1e9:.2f}B",
      "Profitability")

    s("ROA improving YoY",
      roa > roa_prior,
      f"{roa*100:.1f}% vs {roa_prior*100:.1f}% prior",
      "Profitability")

    accruals = ocf / total_assets
    s("Cash earnings quality (OCF/TA > ROA)",
      accruals > roa,
      f"OCF/TA {accruals*100:.1f}% vs ROA {roa*100:.1f}%",
      "Profitability")

    # ── Leverage & Liquidity ──────────────────────────────────────────────────
    s("Leverage decreasing (D/E ↓)",
      debt_to_equity < debt_to_equity_prior,
      f"{debt_to_equity:.2f} vs {debt_to_equity_prior:.2f} prior",
      "Leverage")

    s("Liquidity improving (Current Ratio ↑)",
      current_ratio > current_ratio_prior,
      f"{current_ratio:.2f} vs {current_ratio_prior:.2f} prior",
      "Leverage")

    s("No new share dilution",
      shares <= shares_prior * 1.01,   # allow 1% tolerance
      f"{shares:.0f}M vs {shares_prior:.0f}M prior",
      "Leverage")

    # ── Operating Efficiency ──────────────────────────────────────────────────
    s("Gross margin improving",
      gross_margin > gross_margin_prior,
      f"{gross_margin*100:.1f}% vs {gross_margin_prior*100:.1f}% prior",
      "Efficiency")

    s("Asset turnover improving",
      asset_turnover > asset_turnover_prior,
      f"{asset_turnover:.3f}x vs {asset_turnover_prior:.3f}x prior",
      "Efficiency")

    score = sum(1 for sg in sigs if sg.passed)
    if score >= 7:
        grade = "Strong (7-9)"
    elif score >= 4:
        grade = "Neutral (4-6)"
    else:
        grade = "Weak (0-3)"

    return PiotroskiResult(
        ticker=ticker,
        score=score,
        grade=grade,
        signals=sigs,
        notes=notes or [],
    )
