# keyword_research.py — Keyword opportunity & market analysis module

"""
Aggregates the scored product data + extracted keywords into actionable
seller insights modelled after tools like Helium10 and Jungle Scout.

Outputs a KeywordReport dataclass containing:
  - top_keywords:       best keyword opportunities ranked by importance
  - difficulty_table:   DataFrame of keyword difficulty per keyword
  - price_sweet_spot:   price range where top-ranking products cluster
  - title_patterns:     keywords more common in top-ranked vs bottom-ranked listings
  - competitor_gaps:    keywords in top products missing from others (gap opportunities)
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import numpy as np

from amazon_keyword_tool.analysis.keyword_extractor import (
    KeywordInfo,
    extract_keywords,
    keyword_frequency_by_rank,
)
from amazon_keyword_tool.analysis.scoring import score_products
from amazon_keyword_tool.config import NGRAM_RANGE, TOP_KEYWORDS_N

logger = logging.getLogger(__name__)


# ── Difficulty scoring ────────────────────────────────────────────────────────

def _keyword_difficulty(products_with_kw: pd.DataFrame) -> float:
    """
    Estimate how hard it is to rank for a keyword based on the competing
    products that already contain it in their title.

    Difficulty ∈ [0, 100]:
      - High review counts in top products → harder
      - High ratings in top products       → harder

    Formula: weighted harmonic of normalised reviews × satisfaction
    """
    if products_with_kw.empty:
        return 0.0

    rc  = products_with_kw["review_count"].dropna()
    rat = products_with_kw["rating"].dropna()

    # Normalise review count: 10k+ reviews → 100 difficulty
    avg_rc = float(rc.mean()) if not rc.empty else 0.0
    rc_difficulty = min(math.log1p(avg_rc) / math.log1p(10_000) * 100, 100)

    # Rating: avg ≥ 4.5 → max difficulty contribution
    avg_rat = float(rat.mean()) if not rat.empty else 3.5
    rat_difficulty = max(0.0, (avg_rat - 3.0) / 2.0 * 100)

    # 60% review-based, 40% rating-based
    return round(0.60 * rc_difficulty + 0.40 * rat_difficulty, 1)


# ── Price sweet spot ──────────────────────────────────────────────────────────

def _price_sweet_spot(df: pd.DataFrame, top_n_rank: int = 10) -> dict:
    """
    Find the price range where top-ranking products concentrate.

    Returns a dict with: low, high, median, mean (all as floats in base currency).
    """
    top_df = df[df["rank_position"] <= top_n_rank]["price"].dropna()
    if top_df.empty:
        all_prices = df["price"].dropna()
        top_df = all_prices if not all_prices.empty else pd.Series([0])

    p25  = float(np.percentile(top_df, 25))
    p75  = float(np.percentile(top_df, 75))
    med  = float(top_df.median())
    mean = float(top_df.mean())

    return {
        "low":    round(p25, 2),
        "high":   round(p75, 2),
        "median": round(med, 2),
        "mean":   round(mean, 2),
        "note":   f"Top-{top_n_rank} products cluster between {p25:,.0f}–{p75:,.0f}",
    }


# ── Competitor gap keywords ───────────────────────────────────────────────────

def _competitor_gaps(df: pd.DataFrame, top_n_rank: int = 5) -> list[str]:
    """
    Find keywords present in top-ranked products but rare in the rest.
    These represent 'gap' opportunities — terms a new listing could target
    to differentiate from mid/lower ranked competitors.

    Returns a list of gap keywords sorted by opportunity score.
    """
    top_df  = df[df["rank_position"] <= top_n_rank]
    rest_df = df[df["rank_position"] >  top_n_rank]

    if top_df.empty:
        return []

    freq_compare = keyword_frequency_by_rank(
        df,
        top_n=30,
        rank_threshold=top_n_rank,
    )

    if freq_compare.empty or "keyword" not in freq_compare.columns:
        return []

    # Gap keywords: high presence in top, low presence in bottom
    gaps = freq_compare[
        (freq_compare["top_pct"] >= 30) &
        (freq_compare["bottom_pct"] <= 20) &
        (freq_compare["gap"] >= 15)
    ]["keyword"].tolist()

    return gaps


# ── Main report dataclass ─────────────────────────────────────────────────────

@dataclass
class KeywordReport:
    """Complete keyword research output for one search keyword."""
    search_keyword:     str
    total_products:     int
    top_keywords:       list[KeywordInfo] = field(default_factory=list)
    difficulty_table:   pd.DataFrame      = field(default_factory=pd.DataFrame)
    price_sweet_spot:   dict              = field(default_factory=dict)
    title_patterns:     pd.DataFrame      = field(default_factory=pd.DataFrame)
    competitor_gaps:    list[str]         = field(default_factory=list)
    scored_products_df: pd.DataFrame      = field(default_factory=pd.DataFrame)

    def summary(self) -> str:
        lines = [
            f"\n{'='*70}",
            f"  KEYWORD RESEARCH REPORT: '{self.search_keyword}'",
            f"  Products analysed: {self.total_products}",
            f"{'='*70}",
        ]
        if self.price_sweet_spot:
            ps = self.price_sweet_spot
            lines.append(
                f"\n  Price Sweet Spot (top-10 products): "
                f"{ps['low']:,.0f} – {ps['high']:,.0f}  "
                f"(median: {ps['median']:,.0f})"
            )
        if self.top_keywords:
            lines.append(f"\n  Top Keyword Opportunities (by importance):")
            lines.append(f"  {'Keyword':<35} {'Import.':>7}  {'Freq':>5}  {'AvgRank':>8}  {'Difficulty':>10}")
            lines.append("  " + "-" * 68)
            for kw in self.top_keywords[:15]:
                diff = "--"
                if not self.difficulty_table.empty and "keyword" in self.difficulty_table.columns:
                    row = self.difficulty_table[self.difficulty_table["keyword"] == kw.keyword]
                    if not row.empty:
                        diff = f"{row.iloc[0]['difficulty']:.0f}/100"
                lines.append(
                    f"  {kw.keyword:<35} {kw.importance:>7.3f}  "
                    f"{kw.frequency:>5}  {kw.avg_rank:>8.1f}  {diff:>10}"
                )
        if self.competitor_gaps:
            lines.append(f"\n  Competitor Gap Keywords (found in top listings, rare in others):")
            for g in self.competitor_gaps[:10]:
                lines.append(f"    • {g}")
        lines.append(f"\n{'='*70}\n")
        return "\n".join(lines)


# ── Main analysis function ────────────────────────────────────────────────────

def analyze_keywords(df: pd.DataFrame, search_keyword: str) -> KeywordReport:
    """
    Run the full keyword research pipeline on a cleaned products DataFrame.

    Steps:
      1. Score all products with the A9 composite scorer
      2. Extract keywords from titles via TF-IDF + n-grams
      3. Compute keyword difficulty for top keywords
      4. Calculate price sweet spot from top-ranked products
      5. Find title patterns (top-ranked vs bottom-ranked)
      6. Identify competitor gap keywords

    Args:
        df:             Cleaned products DataFrame (from data_cleaning.clean_products)
        search_keyword: The search term used to produce this page of results

    Returns:
        KeywordReport with all analysis sections populated
    """
    if df.empty:
        logger.warning("analyze_keywords: empty DataFrame.")
        return KeywordReport(
            search_keyword=search_keyword,
            total_products=0,
        )

    logger.info(f"Analysing keyword: '{search_keyword}' over {len(df)} products ...")

    # 1. A9 scoring
    scored_df = score_products(df, keyword=search_keyword)

    # 2. Keyword extraction
    keywords = extract_keywords(
        scored_df,
        ngram_range=NGRAM_RANGE,
        top_n=TOP_KEYWORDS_N,
    )

    # 3. Keyword difficulty
    difficulty_rows = []
    for kw_info in keywords:
        kw = kw_info.keyword
        # Find products whose title contains this keyword
        mask = scored_df["title"].str.contains(
            re.escape(kw) if len(kw) > 1 else kw,
            case=False,
            na=False,
            regex=False,
        )
        subset   = scored_df[mask]
        diff     = _keyword_difficulty(subset)
        avg_a9   = float(subset["a9_score"].mean()) if not subset.empty else 0.0
        difficulty_rows.append({
            "keyword":    kw,
            "difficulty": diff,
            "avg_a9_score": round(avg_a9, 4),
            "product_count": len(subset),
        })

    difficulty_df = pd.DataFrame(difficulty_rows)

    # 4. Price sweet spot
    price_sweet_spot = _price_sweet_spot(scored_df)

    # 5. Title patterns (top vs bottom)
    title_patterns = keyword_frequency_by_rank(scored_df, top_n=15)

    # 6. Competitor gap keywords
    gap_keywords = _competitor_gaps(scored_df)

    return KeywordReport(
        search_keyword=search_keyword,
        total_products=len(scored_df),
        top_keywords=keywords,
        difficulty_table=difficulty_df,
        price_sweet_spot=price_sweet_spot,
        title_patterns=title_patterns,
        competitor_gaps=gap_keywords,
        scored_products_df=scored_df,
    )


# Needed for title contains check
import re
