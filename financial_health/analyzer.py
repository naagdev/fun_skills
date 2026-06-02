"""
Financial health analyzer — fetches key metrics via yfinance and
produces a scored investment-readiness report.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Optional

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    sys.exit("Missing dependencies. Run: pip install -r financial_health/requirements.txt")


# ---------------------------------------------------------------------------
# Scoring thresholds
# ---------------------------------------------------------------------------

THRESHOLDS = {
    # (metric_key, label, weight, good_min, good_max, warning_min, warning_max)
    # weight sums to 100
    "current_ratio":    ("Current Ratio",        10,  1.5, None,  1.0, None),
    "quick_ratio":      ("Quick Ratio",           8,   1.0, None,  0.7, None),
    "debt_to_equity":   ("Debt / Equity",         12,  None, 1.0,  None, 2.0),
    "interest_coverage":("Interest Coverage",     8,   5.0, None,  2.0, None),
    "net_margin":       ("Net Profit Margin",     12,  0.10, None,  0.04, None),
    "roe":              ("Return on Equity",      10,  0.15, None,  0.08, None),
    "roa":              ("Return on Assets",      8,   0.07, None,  0.03, None),
    "revenue_growth":   ("Revenue Growth (YoY)",  12,  0.05, None,  0.00, None),
    "pe_ratio":         ("P/E Ratio",             10,  None, 25.0,  None, 40.0),
    "fcf_margin":       ("FCF / Revenue",         10,  0.08, None,  0.02, None),
}


@dataclass
class MetricResult:
    label: str
    value: Optional[float]
    score: float          # 0-100
    status: str           # "good" | "warning" | "poor" | "n/a"
    weight: int


@dataclass
class HealthReport:
    ticker: str
    company_name: str
    sector: str
    industry: str
    market_cap: Optional[float]
    currency: str
    metrics: list[MetricResult] = field(default_factory=list)
    analyst_recommendation: Optional[str] = None
    target_price: Optional[float]  = None
    current_price: Optional[float] = None
    overall_score: float = 0.0
    grade: str = "N/A"
    summary: str = ""


def _safe(info: dict, *keys, default=None):
    for k in keys:
        v = info.get(k)
        if v is not None and v != "N/A":
            return v
    return default


def _score_metric(value: float, good_min, good_max, warn_min, warn_max) -> tuple[float, str]:
    """Return (score 0-100, status) for a single metric value."""
    if value is None:
        return 0.0, "n/a"

    # Determine "good" direction
    if good_min is not None:
        if value >= good_min:
            return 100.0, "good"
        elif warn_min is not None and value >= warn_min:
            ratio = (value - warn_min) / (good_min - warn_min)
            return round(40 + 60 * ratio, 1), "warning"
        else:
            return 10.0, "poor"

    if good_max is not None:
        if value <= good_max:
            return 100.0, "good"
        elif warn_max is not None and value <= warn_max:
            ratio = (warn_max - value) / (warn_max - good_max)
            return round(40 + 60 * ratio, 1), "warning"
        else:
            return 10.0, "poor"

    return 50.0, "n/a"


def _revenue_growth(ticker_obj) -> Optional[float]:
    try:
        financials = ticker_obj.financials
        if financials is None or financials.empty:
            return None
        rev_row = financials.loc["Total Revenue"] if "Total Revenue" in financials.index else None
        if rev_row is None or len(rev_row) < 2:
            return None
        latest, prior = float(rev_row.iloc[0]), float(rev_row.iloc[1])
        if prior == 0:
            return None
        return (latest - prior) / abs(prior)
    except Exception:
        return None


def _fcf_margin(info: dict, ticker_obj) -> Optional[float]:
    try:
        fcf = _safe(info, "freeCashflow")
        rev = _safe(info, "totalRevenue")
        if fcf and rev and rev != 0:
            return fcf / rev
        cf = ticker_obj.cashflow
        fin = ticker_obj.financials
        if cf is not None and not cf.empty and fin is not None and not fin.empty:
            capex_row = cf.loc["Capital Expenditure"] if "Capital Expenditure" in cf.index else None
            op_row = cf.loc["Operating Cash Flow"] if "Operating Cash Flow" in cf.index else None
            rev_row = fin.loc["Total Revenue"] if "Total Revenue" in fin.index else None
            if capex_row is not None and op_row is not None and rev_row is not None:
                fcf_val = float(op_row.iloc[0]) + float(capex_row.iloc[0])  # capex is negative
                rev_val = float(rev_row.iloc[0])
                if rev_val != 0:
                    return fcf_val / rev_val
    except Exception:
        pass
    return None


def _info_from_static(ticker_symbol: str) -> dict:
    """Return static cached data for *ticker_symbol*, or {} if not available."""
    try:
        from .static_data import STATIC
        entry = STATIC.get(ticker_symbol.upper(), {})
        if not entry:
            return {}
        info = {k: v for k, v in entry.items() if not k.startswith("_")}
        # Translate private convenience keys back to yfinance field names
        if "_debtToEquity_raw" in entry:
            info["debtToEquity"] = entry["_debtToEquity_raw"] * 100  # code divides by 100
        if "_ebitda" in entry and "_interestExpense" in entry:
            info["ebitda"] = entry["_ebitda"]
            info["interestExpense"] = entry["_interestExpense"]
        if "_fcfMarginDirect" in entry:
            info["_fcfMarginDirect"] = entry["_fcfMarginDirect"]
        info["_note"] = entry.get("_note", "")
        info["_source"] = "static"
        return info
    except Exception:
        return {}


def analyze(ticker_symbol: str) -> HealthReport:
    """Fetch data and return a HealthReport for *ticker_symbol*."""
    info: dict = {}
    source = "live"

    try:
        t = yf.Ticker(ticker_symbol.upper())
        fetched = t.info or {}
        if fetched.get("regularMarketPrice") or fetched.get("currentPrice"):
            info = fetched
    except Exception:
        pass

    if not info:
        info = _info_from_static(ticker_symbol)
        source = info.get("_source", "static")
        t = None  # no live object available

    name     = _safe(info, "longName", "shortName") or ticker_symbol.upper()
    sector   = _safe(info, "sector")   or "Unknown"
    industry = _safe(info, "industry") or "Unknown"
    mktcap   = _safe(info, "marketCap")
    currency = _safe(info, "currency") or "USD"
    curr_px  = _safe(info, "currentPrice", "regularMarketPrice")
    tgt_px   = _safe(info, "targetMeanPrice")
    rec      = _safe(info, "recommendationKey")

    def _interest_coverage(i):
        ebitda = _safe(i, "ebitda")
        intexp = _safe(i, "interestExpense")
        if ebitda and intexp and intexp != 0:
            return abs(ebitda / intexp)
        return None

    fcm = info.get("_fcfMarginDirect") or (
        _fcf_margin(info, t) if t is not None else None
    )

    raw: dict[str, Optional[float]] = {
        "current_ratio":     _safe(info, "currentRatio"),
        "quick_ratio":       _safe(info, "quickRatio"),
        "debt_to_equity":    (lambda v: v / 100 if v else None)(_safe(info, "debtToEquity")),
        "interest_coverage": _interest_coverage(info),
        "net_margin":        _safe(info, "profitMargins"),
        "roe":               _safe(info, "returnOnEquity"),
        "roa":               _safe(info, "returnOnAssets"),
        "revenue_growth":    _safe(info, "revenueGrowth") or (
            _revenue_growth(t) if t is not None else None
        ),
        "pe_ratio":          _safe(info, "trailingPE", "forwardPE"),
        "fcf_margin":        fcm,
    }

    metrics: list[MetricResult] = []
    weighted_score = 0.0
    total_weight   = 0

    for key, (label, weight, good_min, good_max, warn_min, warn_max) in THRESHOLDS.items():
        value = raw.get(key)
        score, status = _score_metric(value, good_min, good_max, warn_min, warn_max)
        if status != "n/a":
            weighted_score += score * weight
            total_weight   += weight
        metrics.append(MetricResult(label=label, value=value, score=score,
                                    status=status, weight=weight))

    overall = round(weighted_score / total_weight, 1) if total_weight else 0.0

    if overall >= 75:
        grade, verdict = "A", "Strong financial health — good investment candidate."
    elif overall >= 60:
        grade, verdict = "B", "Above-average health — proceed with further due diligence."
    elif overall >= 45:
        grade, verdict = "C", "Mixed signals — significant risks present; caution advised."
    elif overall >= 30:
        grade, verdict = "D", "Weak financials — high risk; not suitable for most investors."
    else:
        grade, verdict = "F", "Poor financial health — avoid unless speculative risk is intentional."

    report = HealthReport(
        ticker=ticker_symbol.upper(),
        company_name=name,
        sector=sector,
        industry=industry,
        market_cap=mktcap,
        currency=currency,
        metrics=metrics,
        analyst_recommendation=rec,
        target_price=tgt_px,
        current_price=curr_px,
        overall_score=overall,
        grade=grade,
        summary=verdict,
    )
    meta = {"source": source, "note": info.get("_note", "")}
    return report, meta
