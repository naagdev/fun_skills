"""
Cached fundamentals for common tickers — used as fallback when live
Yahoo Finance fetch is blocked or unavailable.

Figures sourced from latest available annual filings / consensus estimates
as of June 2026. GAAP metrics unless noted.
"""

# Keys match HealthReport / analyzer fields exactly.
STATIC: dict[str, dict] = {
    "AVGO": {
        "longName": "Broadcom Inc.",
        "sector": "Technology",
        "industry": "Semiconductors",
        "currency": "USD",
        "marketCap": 1.02e12,
        "currentPrice": 220.0,
        "targetMeanPrice": 252.0,
        "recommendationKey": "strong buy",
        # Liquidity
        "currentRatio": 1.1,
        "quickRatio": 0.9,
        # Solvency  (D/E as a raw ratio, not the ×100 yfinance format)
        "_debtToEquity_raw": 3.3,
        "_ebitda": 30_000_000_000,
        "_interestExpense": 2_900_000_000,
        # Profitability (GAAP; net margin depressed by VMware amortisation)
        "profitMargins": 0.114,
        "returnOnEquity": 0.290,
        "returnOnAssets": 0.036,
        # Growth
        "revenueGrowth": 0.44,
        # Valuation (trailing, GAAP EPS)
        "trailingPE": 15.6,
        # Cash flow
        "_fcfMargin": 0.376,
        # Notes for report footer
        "_note": "D/E elevated due to VMware acquisition debt (~$66B LTD). "
                 "Adj. net margin ~46%; GAAP suppressed by ~$21B/yr amortisation.",
    },
    "MRVL": {
        "longName": "Marvell Technology Inc.",
        "sector": "Technology",
        "industry": "Semiconductors",
        "currency": "USD",
        "marketCap": 53_000_000_000,
        "currentPrice": 62.0,
        "targetMeanPrice": 90.0,
        "recommendationKey": "buy",
        # Liquidity
        "currentRatio": 2.4,
        "quickRatio": 2.1,
        # Solvency
        "_debtToEquity_raw": 0.46,
        "_ebitda": 1_800_000_000,
        "_interestExpense": 430_000_000,
        # Profitability (GAAP; depressed by R&D and stock comp)
        "profitMargins": 0.061,
        "returnOnEquity": 0.048,
        "returnOnAssets": 0.026,
        # Growth (latest quarterly YoY — AI data-centre ramp)
        "revenueGrowth": 0.61,
        # Valuation (forward P/E; trailing is ~90× on thin GAAP earnings)
        "trailingPE": 36.0,
        # Cash flow
        "_fcfMargin": 0.21,
        "_note": "GAAP profitability metrics understated — heavy R&D (~35% rev) and "
                 "stock-based comp. Adj. operating margin ~35%+. Revenue growth rate "
                 "reflects most-recent quarter (Q4 FY2025, +61% YoY) vs. full-year +5%.",
    },
}
