"""
Orchestrates all 5 quant models and prints a consolidated hedge-fund-style report.
"""

from __future__ import annotations

from .dcf import run_dcf
from .monte_carlo import run_monte_carlo
from .piotroski import run_piotroski
from .altman import run_altman
from .kelly import run_kelly

try:
    from colorama import Fore, Style
    C = True
except ImportError:
    C = False

try:
    from tabulate import tabulate
    TAB = True
except ImportError:
    TAB = False


def _g(t, s="good"):   # colored text
    if not C: return t
    color = {"good": Fore.GREEN, "warn": Fore.YELLOW, "poor": Fore.RED,
             "head": Fore.CYAN + Style.BRIGHT, "bold": Style.BRIGHT}.get(s, "")
    return f"{color}{t}{Style.RESET_ALL}"


def _sep(char="=", n=66):
    return char * n


def run_full_analysis(ticker: str, static: dict, portfolio_size: float = 5000.0):
    dcf_cfg = static.get("_dcf", {})
    pio_cfg = static.get("_piotroski", {})
    alt_cfg = static.get("_altman", {})
    kel_cfg = static.get("_kelly", {})

    price = static.get("currentPrice", 0.0)
    target = static.get("targetMeanPrice", price)

    # ── 1. DCF ────────────────────────────────────────────────────────────────
    dcf = run_dcf(
        ticker=ticker,
        fcf=dcf_cfg["fcf_b"] * 1e9,
        shares=dcf_cfg["shares_m"] * 1e6,
        net_debt=dcf_cfg["net_debt_b"] * 1e9,
        current_price=price,
        stage1_growth=dcf_cfg["stage1_growth"],
        stage2_growth=dcf_cfg["stage2_growth"],
        wacc=dcf_cfg["wacc"],
        terminal_growth=dcf_cfg["terminal_growth"],
    )

    # ── 2. Monte Carlo ────────────────────────────────────────────────────────
    mc = run_monte_carlo(
        ticker=ticker,
        fcf=dcf_cfg["fcf_b"] * 1e9,
        shares=dcf_cfg["shares_m"] * 1e6,
        net_debt=dcf_cfg["net_debt_b"] * 1e9,
        current_price=price,
        base_g1=dcf_cfg["stage1_growth"],
        base_g2=dcf_cfg["stage2_growth"],
        base_wacc=dcf_cfg["wacc"],
        terminal_growth=dcf_cfg["terminal_growth"],
        n=10_000,
    )

    # ── 3. Piotroski ──────────────────────────────────────────────────────────
    pio = run_piotroski(
        ticker=ticker,
        roa=pio_cfg["roa"],
        roa_prior=pio_cfg["roa_prior"],
        ocf=pio_cfg["ocf_b"] * 1e9,
        total_assets=pio_cfg["total_assets_b"] * 1e9,
        debt_to_equity=pio_cfg["debt_to_equity"],
        debt_to_equity_prior=pio_cfg["debt_to_equity_prior"],
        current_ratio=pio_cfg["current_ratio"],
        current_ratio_prior=pio_cfg["current_ratio_prior"],
        shares=pio_cfg["shares_m"],
        shares_prior=pio_cfg["shares_m_prior"],
        gross_margin=pio_cfg["gross_margin"],
        gross_margin_prior=pio_cfg["gross_margin_prior"],
        asset_turnover=pio_cfg["asset_turnover"],
        asset_turnover_prior=pio_cfg["asset_turnover_prior"],
        notes=pio_cfg.get("notes"),
    )

    # ── 4. Altman ─────────────────────────────────────────────────────────────
    alt = run_altman(
        ticker=ticker,
        working_capital=alt_cfg["working_capital_b"] * 1e9,
        total_assets=alt_cfg["total_assets_b"] * 1e9,
        retained_earnings=alt_cfg["retained_earnings_b"] * 1e9,
        ebit=alt_cfg["ebit_b"] * 1e9,
        market_cap=alt_cfg["market_cap_b"] * 1e9,
        total_liabilities=alt_cfg["total_liabilities_b"] * 1e9,
    )

    # ── 5. Kelly ──────────────────────────────────────────────────────────────
    kel = run_kelly(
        ticker=ticker,
        current_price=price,
        target_price=target,
        expected_downside=kel_cfg["expected_downside"],
        win_probability=kel_cfg["win_probability"],
        portfolio_size=portfolio_size,
    )

    return dcf, mc, pio, alt, kel


# ─────────────────────────────────────────────────────────────────────────────
# Printers
# ─────────────────────────────────────────────────────────────────────────────

def print_dcf(dcf):
    s = _sep()
    print(f"\n{s}")
    print(_g(f"  MODEL 1 — DCF (2-Stage Discounted Cash Flow)  [{dcf.ticker}]", "head"))
    print(s)
    arrow = "↑" if dcf.upside_pct >= 0 else "↓"
    col   = "good" if dcf.upside_pct >= 0 else "poor"
    print(f"  FCF used        : ${dcf.fcf_used/1e9:.2f}B")
    print(f"  Assumptions     : WACC {dcf.wacc*100:.0f}%  |  "
          f"Stage-1 growth {dcf.stage1_growth*100:.0f}%  |  "
          f"Stage-2 growth {dcf.stage2_growth*100:.0f}%  |  "
          f"Terminal {dcf.terminal_growth*100:.0f}%")
    print(f"  Base Fair Value : ${dcf.fair_value:.2f}  "
          f"(Current ${dcf.current_price:.2f}  "
          f"{_g(f'{arrow} {abs(dcf.upside_pct):.1f}%', col)})")
    print()
    print(_g("  Sensitivity Table — Fair Value per Share ($)", "bold"))
    print("  Rows = Stage-1 Growth  |  Cols = WACC")
    print()

    waccs   = sorted(set(w for w, _ in dcf.sensitivity))
    growths = sorted(set(g for _, g in dcf.sensitivity))

    header = ["Growth \\ WACC"] + [f"{w*100:.0f}%" for w in waccs]
    rows = []
    for g in growths:
        row = [f"{g*100:.0f}%"]
        for w in waccs:
            fv = dcf.sensitivity.get((w, g), 0)
            marker = " ◀" if abs(w - dcf.wacc) < 0.001 and abs(g - dcf.stage1_growth) < 0.001 else ""
            cell = f"${fv:.0f}{marker}"
            color = "good" if fv > dcf.current_price * 1.10 else (
                    "warn" if fv >= dcf.current_price * 0.90 else "poor")
            row.append(_g(cell, color))
        rows.append(row)

    if TAB:
        print("  " + tabulate(rows, headers=header, tablefmt="simple").replace("\n", "\n  "))
    else:
        print("  " + "  ".join(f"{h:>10}" for h in header))
        for row in rows:
            print("  " + "  ".join(f"{c:>10}" for c in row))
    print()


def print_monte_carlo(mc):
    s = _sep()
    print(f"\n{s}")
    print(_g(f"  MODEL 2 — Monte Carlo DCF  [{mc.ticker}]  (N={mc.n_simulations:,})", "head"))
    print(s)
    print(f"  Bear  (P10) : ${mc.p10:>8.2f}")
    print(f"  Low   (P25) : ${mc.p25:>8.2f}")
    print(f"  Median      : ${mc.median:>8.2f}    Mean: ${mc.mean:.2f}")
    print(f"  High  (P75) : ${mc.p75:>8.2f}")
    print(f"  Bull  (P90) : ${mc.p90:>8.2f}")
    print()
    pu = mc.prob_undervalued
    p2 = mc.prob_20pct_upside
    pl = mc.prob_loss
    print(f"  P(stock is undervalued)       : {_g(f'{pu:.1f}%', 'good' if pu>60 else 'warn')}")
    print(f"  P(≥20% upside to fair value)  : {_g(f'{p2:.1f}%', 'good' if p2>50 else 'warn')}")
    print(f"  P(fair value <10% below price): {_g(f'{pl:.1f}%', 'good' if pl<20 else 'poor')}")
    print()


def print_piotroski(pio):
    s = _sep()
    print(f"\n{s}")
    print(_g(f"  MODEL 3 — Piotroski F-Score  [{pio.ticker}]", "head"))
    print(s)
    sc_col = "good" if pio.score >= 7 else ("warn" if pio.score >= 4 else "poor")
    print(f"  Score : {_g(str(pio.score), sc_col)} / 9   —  {_g(pio.grade, sc_col)}")
    print()

    pillar = None
    for sig in pio.signals:
        if sig.pillar != pillar:
            pillar = sig.pillar
            print(f"  {_g(pillar, 'bold')}")
        icon  = _g("✔", "good") if sig.passed else _g("✘", "poor")
        label = f"{sig.name:<40}"
        print(f"    {icon}  {label}  {sig.value}")
    print()
    for note in pio.notes:
        print(f"  ⓘ  {note}")
    if pio.notes:
        print()


def print_altman(alt):
    s = _sep()
    print(f"\n{s}")
    print(_g(f"  MODEL 4 — Altman Z''-Score  [{alt.ticker}]", "head"))
    print(s)
    zone_col = {"Safe": "good", "Grey": "warn", "Distress": "poor"}.get(alt.zone, "warn")
    print(f"  Z''-Score : {_g(f'{alt.z_score:.3f}', zone_col)}   Zone: {_g(alt.zone.upper(), zone_col)}")
    print(f"             (Safe > 2.60  |  Grey 1.10–2.60  |  Distress < 1.10)")
    print()
    rows = [[c.name, f"{c.coefficient:.2f}", f"{c.ratio:.4f}", f"{c.contribution:+.4f}"]
            for c in alt.components]
    if TAB:
        tbl = tabulate(rows, headers=["Component", "Coeff", "Ratio", "Contribution"],
                       tablefmt="simple", colalign=("left","right","right","right"))
        print("  " + tbl.replace("\n", "\n  "))
    else:
        for r in rows:
            print(f"  {r[0]:<42} {r[1]:>6}  {r[2]:>8}  {r[3]:>8}")
    print()


def print_kelly(kel, all_kelly: list | None = None):
    s = _sep()
    print(f"\n{s}")
    print(_g(f"  MODEL 5 — Kelly Criterion Position Sizing  [{kel.ticker}]", "head"))
    print(s)
    print(f"  Expected upside   : {kel.expected_upside*100:+.1f}%  "
          f"(${kel.current_price:.2f} → ${kel.target_price:.2f})")
    print(f"  Expected downside : −{kel.expected_downside*100:.0f}% (bear case)")
    print(f"  Win probability   : {kel.win_probability*100:.0f}%")
    print(f"  Win / Loss ratio  : {kel.b_ratio:.2f}x")
    print()
    print(f"  Full Kelly        : {kel.full_kelly_pct:.1f}% of portfolio")
    print(f"  Half Kelly (rec.) : {_g(f'{kel.half_kelly_pct:.1f}%', 'good')} of portfolio  "
          f"→  {_g(f'${kel.dollar_allocation:,.0f}', 'good')} of ${kel.portfolio_size:,.0f}")
    print()

    if all_kelly and len(all_kelly) > 1:
        total_alloc = sum(k.dollar_allocation for k in all_kelly)
        cash = kel.portfolio_size - total_alloc
        print(_g("  Portfolio Allocation Summary", "bold"))
        for k in all_kelly:
            bar_len = int(k.dollar_allocation / kel.portfolio_size * 40)
            print(f"    {k.ticker:<6}  {'█' * bar_len:<40}  ${k.dollar_allocation:>6,.0f}  "
                  f"({k.half_kelly_pct:.1f}%)")
        cash_bar = int(max(0, cash) / kel.portfolio_size * 40)
        print(f"    {'CASH':<6}  {'░' * cash_bar:<40}  ${max(0,cash):>6,.0f}  "
              f"({max(0,cash)/kel.portfolio_size*100:.1f}%)")
        print()
        print(f"  ⓘ  Kelly keeps {max(0,cash)/kel.portfolio_size*100:.1f}% in cash/other — "
              f"by design, full deployment into two correlated semis is suboptimal.")
    print()


def print_full_summary(results: list[tuple]):
    """
    results = [(ticker, health_score, health_grade, dcf, mc, pio, alt, kel), ...]
    """
    s = _sep("═")
    print(f"\n{s}")
    print(_g("  CONSOLIDATED INVESTMENT SUMMARY", "head"))
    print(s)
    header = ["", "Health", "DCF Fair Value", "MC Median", "P(Undervalued)",
              "Piotroski", "Altman Z''", "Half-Kelly $"]
    rows = []
    for ticker, hs, hg, dcf, mc, pio, alt, kel in results:
        hcol  = "good" if hs >= 70 else ("warn" if hs >= 50 else "poor")
        dcol  = "good" if dcf.upside_pct >= 10 else ("warn" if dcf.upside_pct >= 0 else "poor")
        pcol  = "good" if mc.prob_undervalued >= 60 else "warn"
        zcol  = {"Safe": "good", "Grey": "warn", "Distress": "poor"}.get(alt.zone, "warn")
        rows.append([
            _g(ticker, "bold"),
            _g(f"{hs:.0f}/100 ({hg})", hcol),
            _g(f"${dcf.fair_value:.0f} ({dcf.upside_pct:+.1f}%)", dcol),
            f"${mc.median:.0f}",
            _g(f"{mc.prob_undervalued:.0f}%", pcol),
            _g(f"{pio.score}/9 — {pio.grade.split()[0]}", "good" if pio.score >= 7 else "warn"),
            _g(f"{alt.z_score:.2f} ({alt.zone})", zcol),
            _g(f"${kel.dollar_allocation:,.0f}", "good"),
        ])
    if TAB:
        print("\n  " + tabulate(rows, headers=header, tablefmt="simple").replace("\n", "\n  "))
    else:
        for row in rows:
            print("  ".join(str(c) for c in row))
    print()
