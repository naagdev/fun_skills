"""
Cached fundamentals for common tickers — used as fallback when live
Yahoo Finance fetch is blocked or unavailable.

Figures sourced from latest available annual filings / consensus estimates
as of June 2026. GAAP metrics unless noted.
"""

STATIC: dict[str, dict] = {
    "AVGO": {
        # ── Identity ──────────────────────────────────────────────────────────
        "longName": "Broadcom Inc.",
        "sector": "Technology",
        "industry": "Semiconductors",
        "currency": "USD",
        # ── Market data ───────────────────────────────────────────────────────
        "marketCap": 1.02e12,
        "currentPrice": 220.0,
        "targetMeanPrice": 252.0,
        "recommendationKey": "strong buy",
        # ── Liquidity ─────────────────────────────────────────────────────────
        "currentRatio": 1.1,
        "quickRatio": 0.9,
        # ── Solvency ──────────────────────────────────────────────────────────
        # yfinance reports debtToEquity ×100; code divides by 100
        "debtToEquity": 330.0,
        "ebitda": 30_000_000_000,
        "interestExpense": 2_900_000_000,
        # ── Profitability (GAAP) ──────────────────────────────────────────────
        "profitMargins": 0.114,
        "returnOnEquity": 0.290,
        "returnOnAssets": 0.036,
        # ── Growth ────────────────────────────────────────────────────────────
        "revenueGrowth": 0.44,
        # ── Valuation ─────────────────────────────────────────────────────────
        "trailingPE": 15.6,
        # ── Cash flow ─────────────────────────────────────────────────────────
        "_fcfMarginDirect": 0.376,

        # ── DCF inputs ────────────────────────────────────────────────────────
        "_dcf": {
            "fcf_b": 19.4,           # free cash flow in $B (FY2024)
            "shares_m": 4_770.0,     # shares outstanding in M (post 10:1 split)
            "net_debt_b": 56.0,      # LTD $66B − cash $10B
            "stage1_growth": 0.25,   # 5-yr AI networking + VMware SaaS ramp
            "stage2_growth": 0.13,
            "wacc": 0.09,
            "terminal_growth": 0.03,
        },

        # ── Piotroski inputs ──────────────────────────────────────────────────
        "_piotroski": {
            "roa": 0.036,
            "roa_prior": 0.145,          # FY2023 pre-VMware (structural, not operational decline)
            "ocf_b": 21.4,
            "total_assets_b": 162.0,
            "debt_to_equity": 3.30,
            "debt_to_equity_prior": 4.00,   # right after VMware close
            "current_ratio": 1.1,
            "current_ratio_prior": 0.95,
            "shares_m": 4_770.0,
            "shares_m_prior": 4_760.0,
            "gross_margin": 0.640,
            "gross_margin_prior": 0.610,
            "asset_turnover": 0.318,        # 51.57 / 162
            "asset_turnover_prior": 0.491,  # 35.82 / 73 (FY2023, pre-VMware)
            "notes": [
                "ROA decline and asset-turnover decline are both VMware acquisition artefacts "
                "(asset base doubled); not indicative of operational deterioration.",
            ],
        },

        # ── Altman Z-Score inputs ─────────────────────────────────────────────
        "_altman": {
            "working_capital_b": 1.8,       # current assets $14.9B − current liabilities $13.1B
            "total_assets_b": 162.0,
            "retained_earnings_b": -12.0,   # accumulated deficit from goodwill/amortisation
            "ebit_b": 9.0,                  # GAAP EBIT FY2024
            "market_cap_b": 1_020.0,
            "total_liabilities_b": 141.0,
        },

        # ── Kelly inputs ──────────────────────────────────────────────────────
        "_kelly": {
            "expected_downside": 0.15,      # large-cap, more stable; ~15% bear-case loss
            "win_probability": 0.72,        # Strong Buy consensus + Grade A
        },

        "_note": (
            "D/E elevated due to VMware acquisition debt (~$66B LTD). "
            "Adj. net margin ~46%; GAAP suppressed by ~$21B/yr amortisation."
        ),
    },

    "MRVL": {
        # ── Identity ──────────────────────────────────────────────────────────
        "longName": "Marvell Technology Inc.",
        "sector": "Technology",
        "industry": "Semiconductors",
        "currency": "USD",
        # ── Market data ───────────────────────────────────────────────────────
        "marketCap": 53_000_000_000,
        "currentPrice": 62.0,
        "targetMeanPrice": 90.0,
        "recommendationKey": "buy",
        # ── Liquidity ─────────────────────────────────────────────────────────
        "currentRatio": 2.4,
        "quickRatio": 2.1,
        # ── Solvency ──────────────────────────────────────────────────────────
        "debtToEquity": 46.0,
        "ebitda": 1_800_000_000,
        "interestExpense": 430_000_000,
        # ── Profitability (GAAP) ──────────────────────────────────────────────
        "profitMargins": 0.061,
        "returnOnEquity": 0.048,
        "returnOnAssets": 0.026,
        # ── Growth ────────────────────────────────────────────────────────────
        "revenueGrowth": 0.61,             # Q4 FY2025 YoY; full-year FY25 was +5%
        # ── Valuation ─────────────────────────────────────────────────────────
        "trailingPE": 36.0,
        # ── Cash flow ─────────────────────────────────────────────────────────
        "_fcfMarginDirect": 0.21,

        # ── DCF inputs ────────────────────────────────────────────────────────
        "_dcf": {
            "fcf_b": 1.21,           # FCF FY2025
            "shares_m": 857.0,
            "net_debt_b": 3.6,       # debt $4.7B − cash $1.1B
            "stage1_growth": 0.30,   # AI custom silicon ramp (Amazon, Google XPUs)
            "stage2_growth": 0.15,
            "wacc": 0.11,
            "terminal_growth": 0.03,
        },

        # ── Piotroski inputs ──────────────────────────────────────────────────
        "_piotroski": {
            "roa": 0.026,
            "roa_prior": 0.018,
            "ocf_b": 1.58,
            "total_assets_b": 13.1,
            "debt_to_equity": 0.46,
            "debt_to_equity_prior": 0.52,
            "current_ratio": 2.4,
            "current_ratio_prior": 2.1,
            "shares_m": 857.0,
            "shares_m_prior": 851.0,        # slight creep from stock comp
            "gross_margin": 0.550,
            "gross_margin_prior": 0.520,
            "asset_turnover": 0.440,        # 5.77 / 13.1
            "asset_turnover_prior": 0.441,  # 5.51 / 12.5  (effectively flat)
            "notes": [
                "GAAP ROE/ROA understated — heavy R&D (~35% of revenue) and "
                "stock-based compensation (~$750M/yr) depress net income.",
                "Adj. operating margin >35%; GAAP net margin ~6%.",
            ],
        },

        # ── Altman Z-Score inputs ─────────────────────────────────────────────
        "_altman": {
            "working_capital_b": 1.9,       # current assets $3.2B − current liabilities $1.3B
            "total_assets_b": 13.1,
            "retained_earnings_b": -4.2,    # accumulated deficit from Inphi/Innovium acquisitions
            "ebit_b": 0.50,                 # GAAP EBIT FY2025
            "market_cap_b": 53.0,
            "total_liabilities_b": 6.5,
        },

        # ── Kelly inputs ──────────────────────────────────────────────────────
        "_kelly": {
            "expected_downside": 0.35,      # higher-beta mid-cap semi; ~35% bear-case loss
            "win_probability": 0.65,        # Buy consensus + Grade B
        },

        "_note": (
            "GAAP profitability metrics understated — heavy R&D (~35% rev) and "
            "stock-based comp. Adj. operating margin ~35%+. Revenue growth rate "
            "reflects most-recent quarter (Q4 FY2025, +61% YoY) vs. full-year +5%."
        ),
    },
}
