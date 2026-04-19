# reporting/console.py — Rich terminal output for keyword research reports

"""
Pretty-prints keyword research results to stdout using only stdlib.
Designed for Python 3.10+ f-strings and works without `rich` installed.
"""

import logging
from typing import Optional

import pandas as pd

from amazon_keyword_tool.analysis.keyword_research import KeywordReport

logger = logging.getLogger(__name__)


def _sep(char: str = "─", width: int = 72) -> str:
    return "  " + char * width


def _header(title: str, width: int = 72) -> str:
    pad = max(0, width - len(title) - 2)
    return f"\n  ╔{'═' * (width)}╗\n  ║  {title}{' ' * pad}║\n  ╚{'═' * (width)}╝"


def print_report(report: KeywordReport, currency_symbol: str = "₹") -> None:
    """
    Print a formatted keyword research report to stdout.

    Args:
        report:          KeywordReport from keyword_research.analyze_keywords()
        currency_symbol: Currency symbol for price display (default: ₹ for India)
    """
    # ── Header ────────────────────────────────────────────────────────────────
    print(_header(f"Amazon A9 Keyword Research — '{report.search_keyword}'"))
    print(f"  Products analysed : {report.total_products}")

    # ── Top Keywords Table ────────────────────────────────────────────────────
    if report.top_keywords:
        print(f"\n  {'TOP KEYWORD OPPORTUNITIES':}\n" + _sep())
        header = (
            f"  {'#':>3}  {'Keyword':<32}  {'Score':>6}  "
            f"{'Freq':>5}  {'AvgRank':>8}  {'Difficulty':>10}"
        )
        print(header)
        print(_sep())

        for i, kw in enumerate(report.top_keywords[:20], 1):
            diff_str = "--"
            if not report.difficulty_table.empty and "keyword" in report.difficulty_table.columns:
                row = report.difficulty_table[report.difficulty_table["keyword"] == kw.keyword]
                if not row.empty:
                    diff_val = row.iloc[0]["difficulty"]
                    # Visual difficulty bar
                    bars = int(diff_val / 10)
                    diff_str = f"{'█' * bars}{'░' * (10-bars)} {diff_val:.0f}"

            print(
                f"  {i:>3}. {kw.keyword:<32}  {kw.importance:>6.3f}  "
                f"{kw.frequency:>5}  {kw.avg_rank:>8.1f}  {diff_str}"
            )

    # ── Price Sweet Spot ──────────────────────────────────────────────────────
    if report.price_sweet_spot:
        ps = report.price_sweet_spot
        print(f"\n  {'PRICE SWEET SPOT (top-10 ranked products)':}\n" + _sep())
        print(f"  Optimal range  : {currency_symbol}{ps['low']:,.0f} – {currency_symbol}{ps['high']:,.0f}")
        print(f"  Median price   : {currency_symbol}{ps['median']:,.0f}")
        print(f"  Mean price     : {currency_symbol}{ps['mean']:,.0f}")

    # ── Title Pattern Analysis ────────────────────────────────────────────────
    if not report.title_patterns.empty:
        tp = report.title_patterns
        print(f"\n  {'TITLE KEYWORD PATTERNS (top vs. rest)':}\n" + _sep())
        print(
            f"  {'Keyword':<30}  {'Top%':>6}  {'Rest%':>6}  {'Gap':>6}"
        )
        print(_sep())
        for _, row in tp.head(10).iterrows():
            gap_str = f"+{row['gap']:.1f}" if row["gap"] > 0 else f"{row['gap']:.1f}"
            print(
                f"  {str(row['keyword']):<30}  "
                f"{row['top_pct']:>6.1f}  {row['bottom_pct']:>6.1f}  {gap_str:>6}"
            )

    # ── Competitor Gap Keywords ───────────────────────────────────────────────
    if report.competitor_gaps:
        print(f"\n  {'COMPETITOR GAP KEYWORDS':}\n" + _sep())
        print("  These keywords appear in top listings but are rare in lower-ranked ones:")
        for gap in report.competitor_gaps[:10]:
            print(f"    •  {gap}")

    # ── Top Scored Products ───────────────────────────────────────────────────
    if not report.scored_products_df.empty:
        df = report.scored_products_df
        print(f"\n  {'TOP 10 PRODUCTS BY A9 SCORE':}\n" + _sep())
        print(
            f"  {'#':>3}  {'Title':<45}  {'A9 Score':>9}  {'Rating':>7}  "
            f"{'Reviews':>9}  {'Price':>12}"
        )
        print(_sep())
        for i, (_, row) in enumerate(df.head(10).iterrows(), 1):
            title    = str(row.get("title", ""))[:44]
            a9       = row.get("a9_score", 0.0)
            rating   = f"{row['rating']:.1f}" if pd.notna(row.get("rating")) else "N/A"
            reviews  = f"{int(row['review_count'])}" if pd.notna(row.get("review_count")) else "N/A"
            price    = (
                f"{currency_symbol}{row['price']:,.0f}"
                if pd.notna(row.get("price")) else "N/A"
            )
            print(
                f"  {i:>3}. {title:<45}  {a9:>9.4f}  "
                f"{rating:>7}  {reviews:>9}  {price:>12}"
            )

    print(f"\n{_sep('═')}\n")
