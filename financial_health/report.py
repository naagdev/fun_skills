"""Pretty-print a HealthReport to the terminal."""

from __future__ import annotations

from .analyzer import HealthReport, MetricResult

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def _color(text: str, status: str) -> str:
    if not HAS_COLOR:
        return text
    c = {"good": Fore.GREEN, "warning": Fore.YELLOW, "poor": Fore.RED}.get(status, "")
    return f"{c}{text}{Style.RESET_ALL}"


def _fmt_val(m: MetricResult) -> str:
    if m.value is None:
        return "N/A"
    # Percentage metrics
    pct_keys = {"Net Profit Margin", "Return on Equity", "Return on Assets",
                "Revenue Growth (YoY)", "FCF / Revenue"}
    if m.label in pct_keys:
        return f"{m.value * 100:.1f}%"
    if m.label in {"P/E Ratio"}:
        return f"{m.value:.1f}x"
    return f"{m.value:.2f}"


def _grade_color(grade: str) -> str:
    if not HAS_COLOR:
        return grade
    c = {"A": Fore.GREEN, "B": Fore.CYAN, "C": Fore.YELLOW,
         "D": Fore.RED, "F": Fore.RED + Style.BRIGHT}.get(grade, "")
    return f"{c}{grade}{Style.RESET_ALL}"


def _fmt_mktcap(v) -> str:
    if v is None:
        return "N/A"
    if v >= 1e12:
        return f"${v/1e12:.2f}T"
    if v >= 1e9:
        return f"${v/1e9:.2f}B"
    if v >= 1e6:
        return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"


def print_report(r: HealthReport) -> None:
    sep = "=" * 62

    print(f"\n{sep}")
    print(f"  FINANCIAL HEALTH REPORT — {r.ticker}")
    print(sep)
    print(f"  Company   : {r.company_name}")
    print(f"  Sector    : {r.sector}  |  {r.industry}")
    print(f"  Market Cap: {_fmt_mktcap(r.market_cap)}  ({r.currency})")
    if r.current_price:
        print(f"  Price     : {r.currency} {r.current_price:,.2f}", end="")
        if r.target_price:
            upside = (r.target_price - r.current_price) / r.current_price * 100
            print(f"  →  Target {r.currency} {r.target_price:,.2f}  ({upside:+.1f}%)", end="")
        print()
    if r.analyst_recommendation:
        print(f"  Analyst   : {r.analyst_recommendation.upper()}")
    print()

    rows = []
    for m in r.metrics:
        val_str    = _color(_fmt_val(m), m.status)
        score_str  = _color(f"{m.score:.0f}/100", m.status)
        status_str = _color(m.status.upper(), m.status)
        rows.append([m.label, val_str, score_str, status_str])

    if HAS_TABULATE:
        print(tabulate(rows, headers=["Metric", "Value", "Score", "Status"],
                       tablefmt="simple", colalign=("left", "right", "right", "left")))
    else:
        print(f"{'Metric':<28}{'Value':>10}{'Score':>10}  Status")
        print("-" * 60)
        for label, val, score, status in rows:
            print(f"{label:<28}{val:>10}{score:>10}  {status}")

    print()
    print(sep)
    grade_str = _grade_color(r.grade)
    score_col = _color(f"{r.overall_score:.1f}", "good" if r.overall_score >= 60 else
                       ("warning" if r.overall_score >= 45 else "poor"))
    print(f"  Overall Score : {score_col} / 100   Grade: {grade_str}")
    print(f"  Verdict       : {r.summary}")
    print(sep)
    print()
