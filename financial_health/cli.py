#!/usr/bin/env python3
"""
Usage:
    python -m financial_health <TICKER> [<TICKER> ...]
    python -m financial_health AAPL MSFT TSLA
"""

import sys
from .analyzer import analyze
from .report import print_report


def main():
    tickers = [a.upper() for a in sys.argv[1:] if not a.startswith("-")]
    if not tickers:
        print("Usage: python -m financial_health <TICKER> [TICKER ...]")
        print("Example: python -m financial_health AAPL MSFT GOOGL")
        sys.exit(1)

    for ticker in tickers:
        print(f"\nFetching data for {ticker} …")
        try:
            report = analyze(ticker)
            print_report(report)
        except Exception as e:
            print(f"  Error fetching {ticker}: {e}")


if __name__ == "__main__":
    main()
