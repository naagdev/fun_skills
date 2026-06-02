"""
Cached fundamentals for common tickers — used as fallback when live
Yahoo Finance fetch is blocked or unavailable.

Prices updated June 2026: MRVL $273, AVGO $478.
Fundamentals reflect FY2026 estimates (MRVL FY ends Feb, AVGO FY ends Oct).
GAAP metrics unless noted.
"""

STATIC: dict[str, dict] = {
    "AVGO": {
        # ── Identity ──────────────────────────────────────────────────────────
        "longName": "Broadcom Inc.",
        "sector": "Technology",
        "industry": "Semiconductors",
        "currency": "USD",
        # ── Market data (updated June 2026) ───────────────────────────────────
        "marketCap": 2.28e12,          # 4,770M shares × $478
        "currentPrice": 478.0,
        "targetMeanPrice": 560.0,      # consensus analyst target Jun 2026
        "recommendationKey": "strong buy",
        # ── Liquidity (FY2025, Oct 2025) ─────────────────────────────────────
        "currentRatio": 1.2,
        "quickRatio": 1.0,
        # ── Solvency ──────────────────────────────────────────────────────────
        "debtToEquity": 250.0,         # D/E improving as VMware debt paid down (~2.5x)
        "ebitda": 36_000_000_000,
        "interestExpense": 2_600_000_000,
        # ── Profitability (FY2025 est., GAAP) ────────────────────────────────
        "profitMargins": 0.150,        # improving as VMware amortisation anniversaries off
        "returnOnEquity": 0.350,
        "returnOnAssets": 0.050,
        # ── Growth ────────────────────────────────────────────────────────────
        "revenueGrowth": 0.20,         # FY2025 ~$62B vs FY2024 $51.6B
        # ── Valuation ─────────────────────────────────────────────────────────
        "trailingPE": 28.3,            # $478 / ~$16.9 GAAP EPS
        # ── Cash flow ─────────────────────────────────────────────────────────
        "_fcfMarginDirect": 0.387,     # FCF $24B / rev $62B

        # ── DCF inputs ────────────────────────────────────────────────────────
        "_dcf": {
            "fcf_b": 24.0,             # FY2025 FCF est. ($B)
            "shares_m": 4_770.0,
            "net_debt_b": 48.0,        # LTD ~$58B − cash ~$10B (paid ~$8B down)
            "stage1_growth": 0.25,
            "stage2_growth": 0.13,
            "wacc": 0.09,
            "terminal_growth": 0.03,
        },

        # ── Piotroski inputs (FY2025 vs FY2024) ──────────────────────────────
        "_piotroski": {
            "roa": 0.050,
            "roa_prior": 0.036,            # FY2024 (now improving)
            "ocf_b": 25.0,
            "total_assets_b": 168.0,
            "debt_to_equity": 2.50,
            "debt_to_equity_prior": 3.30,
            "current_ratio": 1.2,
            "current_ratio_prior": 1.1,
            "shares_m": 4_780.0,
            "shares_m_prior": 4_770.0,
            "gross_margin": 0.660,
            "gross_margin_prior": 0.640,
            "asset_turnover": 0.369,       # 62B / 168B
            "asset_turnover_prior": 0.318, # 51.6B / 162B (improving)
            "notes": [
                "ROA and asset-turnover now improving year-over-year as VMware "
                "synergies materialise and debt is paid down.",
            ],
        },

        # ── Altman Z-Score inputs ─────────────────────────────────────────────
        "_altman": {
            "working_capital_b": 3.0,
            "total_assets_b": 168.0,
            "retained_earnings_b": -8.0,   # accumulated deficit shrinking
            "ebit_b": 12.0,
            "market_cap_b": 2_280.0,       # updated
            "total_liabilities_b": 135.0,  # debt paydown
        },

        # ── Kelly inputs ──────────────────────────────────────────────────────
        "_kelly": {
            "expected_downside": 0.20,     # large-cap, still elevated macro risk
            "win_probability": 0.70,
        },

        "_note": (
            "Price updated to $478 (Jun 2026). FY2025 fundamentals estimated. "
            "D/E improving as VMware debt ($66B→~$58B) is paid down. "
            "GAAP net margin expanding as ~$21B/yr amortisation anniversaries roll off."
        ),
    },

    "MRVL": {
        # ── Identity ──────────────────────────────────────────────────────────
        "longName": "Marvell Technology Inc.",
        "sector": "Technology",
        "industry": "Semiconductors",
        "currency": "USD",
        # ── Market data (updated June 2026) ───────────────────────────────────
        "marketCap": 233_961_000_000,  # 857M shares × $273
        "currentPrice": 273.0,
        "targetMeanPrice": 315.0,      # consensus analyst target Jun 2026
        "recommendationKey": "buy",
        # ── Liquidity (FY2026, Feb 2026) ─────────────────────────────────────
        "currentRatio": 2.6,
        "quickRatio": 2.3,
        # ── Solvency ──────────────────────────────────────────────────────────
        "debtToEquity": 35.0,          # D/E ~0.35 as debt paid down
        "ebitda": 3_200_000_000,
        "interestExpense": 390_000_000,
        # ── Profitability (FY2026 est., GAAP) ────────────────────────────────
        "profitMargins": 0.085,        # improving on AI revenue scale
        "returnOnEquity": 0.080,
        "returnOnAssets": 0.048,
        # ── Growth ────────────────────────────────────────────────────────────
        "revenueGrowth": 0.47,         # FY2026 ~$8.5B vs FY2025 $5.77B
        # ── Valuation ─────────────────────────────────────────────────────────
        "trailingPE": 109.0,           # $273 / ~$2.50 GAAP EPS (growth premium)
        # ── Cash flow ─────────────────────────────────────────────────────────
        "_fcfMarginDirect": 0.294,     # FCF $2.5B / rev $8.5B

        # ── DCF inputs ────────────────────────────────────────────────────────
        "_dcf": {
            "fcf_b": 2.5,              # FY2026 FCF est. ($B)
            "shares_m": 857.0,
            "net_debt_b": 2.8,         # debt ~$3.8B − cash ~$1.0B
            "stage1_growth": 0.35,     # higher conviction given AI custom silicon evidence
            "stage2_growth": 0.18,
            "wacc": 0.11,
            "terminal_growth": 0.03,
        },

        # ── Piotroski inputs (FY2026 vs FY2025) ──────────────────────────────
        "_piotroski": {
            "roa": 0.048,
            "roa_prior": 0.026,
            "ocf_b": 3.0,
            "total_assets_b": 15.0,
            "debt_to_equity": 0.35,
            "debt_to_equity_prior": 0.46,
            "current_ratio": 2.6,
            "current_ratio_prior": 2.4,
            "shares_m": 870.0,
            "shares_m_prior": 857.0,       # stock comp creep
            "gross_margin": 0.570,
            "gross_margin_prior": 0.550,
            "asset_turnover": 0.567,       # 8.5B / 15B
            "asset_turnover_prior": 0.440, # 5.77B / 13.1B
            "notes": [
                "All nine signals improving on a trailing basis as AI custom "
                "silicon revenue (Amazon Trainium, Google TPU) scales rapidly.",
                "GAAP profitability still understated vs adj. (~35% adj. op. margin).",
            ],
        },

        # ── Altman Z-Score inputs ─────────────────────────────────────────────
        "_altman": {
            "working_capital_b": 2.5,
            "total_assets_b": 15.0,
            "retained_earnings_b": -2.0,   # accumulated deficit shrinking with profits
            "ebit_b": 0.85,
            "market_cap_b": 234.0,         # updated
            "total_liabilities_b": 6.0,
        },

        # ── Kelly inputs ──────────────────────────────────────────────────────
        "_kelly": {
            "expected_downside": 0.35,     # still high-beta; AI capex slowdown risk
            "win_probability": 0.63,       # strong thesis but valuation now stretched
        },

        "_note": (
            "Price updated to $273 (Jun 2026). FY2026 fundamentals estimated. "
            "Trailing P/E ~109x reflects growth-premium pricing. "
            "Forward P/E ~55x on FY2027 consensus EPS of ~$5. "
            "AI custom silicon (Amazon, Google, Microsoft) driving revenue re-rating."
        ),
    },
}
