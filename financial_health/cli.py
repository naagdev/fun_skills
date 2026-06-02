#!/usr/bin/env python3
"""
Usage:
    python -m financial_health <TICKER> [<TICKER> ...]           # health report
    python -m financial_health <TICKER> [<TICKER> ...] --full    # + 5 quant models
    python -m financial_health MRVL AVGO --full --portfolio 5000
"""

import sys
from .analyzer import analyze
from .report import print_report


def main():
    args = sys.argv[1:]
    full_mode = "--full" in args
    args = [a for a in args if a != "--full"]

    portfolio_size = 5000.0
    if "--portfolio" in args:
        idx = args.index("--portfolio")
        try:
            portfolio_size = float(args[idx + 1])
            args = [a for a in args if a not in ("--portfolio", args[idx + 1])]
        except (IndexError, ValueError):
            pass

    tickers = [a.upper() for a in args if not a.startswith("-")]
    if not tickers:
        print("Usage: python -m financial_health <TICKER> [TICKER ...] [--full] [--portfolio N]")
        print("Example: python -m financial_health MRVL AVGO --full --portfolio 5000")
        sys.exit(1)

    all_reports = []

    for ticker in tickers:
        print(f"\nAnalyzing {ticker} …")
        try:
            report, meta = analyze(ticker)
            print_report(report, note=meta.get("note", ""), source=meta.get("source", "live"))
            all_reports.append((ticker, report, meta))
        except Exception as e:
            print(f"  Error analyzing {ticker}: {e}")
            import traceback; traceback.print_exc()

    if full_mode and all_reports:
        _run_quant_models(all_reports, portfolio_size)


def _run_quant_models(all_reports, portfolio_size):
    try:
        from .static_data import STATIC
        from .models.full_report import (
            run_full_analysis, print_dcf, print_monte_carlo,
            print_piotroski, print_altman, print_kelly, print_full_summary,
        )
    except ImportError as e:
        print(f"\nCould not load quant models: {e}")
        return

    all_kelly  = []
    summaries  = []

    for ticker, report, meta in all_reports:
        static = STATIC.get(ticker.upper())
        if not static:
            print(f"\n  No quant model data for {ticker} — skipping.")
            continue

        print(f"\n{'='*66}")
        print(f"  QUANTITATIVE MODELS — {ticker}")
        print(f"{'='*66}")

        dcf, mc, pio, alt, kel = run_full_analysis(ticker, static, portfolio_size)

        print_dcf(dcf)
        print_monte_carlo(mc)
        print_piotroski(pio)
        print_altman(alt)

        all_kelly.append(kel)
        summaries.append((ticker, report.overall_score, report.grade, dcf, mc, pio, alt, kel))

    # Print Kelly for all tickers together so allocation bar is shown
    for kel in all_kelly:
        print_kelly(kel, all_kelly=all_kelly)
        break   # allocation bar is printed once, inside the first call

    if summaries:
        print_full_summary(summaries)


if __name__ == "__main__":
    main()
