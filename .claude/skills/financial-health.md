# financial-health

Assess a company's financial health before investing. Accepts one or more stock tickers and produces a scored, multi-metric investment-readiness report.

## When to invoke

Use this skill whenever the user asks you to:
- Check the financial health of a company or stock
- Evaluate whether a company is worth investing in
- Compare two or more stocks on financial fundamentals
- Get a quick overview of valuation, profitability, liquidity, or solvency metrics

## Steps

1. **Ensure dependencies are installed**

   ```bash
   pip install -r financial_health/requirements.txt -q
   ```

2. **Run the analyzer** for each requested ticker(s)

   ```bash
   python -m financial_health <TICKER>
   ```

   Multiple tickers at once:
   ```bash
   python -m financial_health AAPL MSFT GOOGL
   ```

3. **Interpret and present the output**

   The tool prints a scored report. Summarize the key findings for the user:
   - Overall score and grade (A–F)
   - Any metrics in "poor" status — these are red flags
   - Price vs. analyst target (upside/downside %)
   - Analyst consensus recommendation
   - A clear invest / watch / avoid recommendation based on the grade:
     - **A / B** → Generally investable; highlight strengths
     - **C** → Caution; list specific risks; suggest monitoring
     - **D / F** → Avoid or speculative only; explain the key weaknesses

## Metrics scored (10 total, weighted)

| Metric | What it measures |
|---|---|
| Current Ratio | Short-term liquidity (≥ 1.5 = good) |
| Quick Ratio | Liquid-only coverage (≥ 1.0 = good) |
| Debt / Equity | Leverage (≤ 1.0 = good) |
| Interest Coverage | Ability to service debt (≥ 5× = good) |
| Net Profit Margin | Bottom-line efficiency (≥ 10% = good) |
| Return on Equity | Shareholder return generation (≥ 15% = good) |
| Return on Assets | Asset utilization (≥ 7% = good) |
| Revenue Growth (YoY) | Business momentum (≥ 5% = good) |
| P/E Ratio | Valuation (≤ 25× = good) |
| FCF / Revenue | Free cash flow quality (≥ 8% = good) |

## Data source

Data is fetched live from Yahoo Finance via the `yfinance` library — no API key needed.

## Example

```
> /financial-health

User: Check Apple's financial health
```

Run:
```bash
python -m financial_health AAPL
```

Then summarize the report in plain language for the user.
