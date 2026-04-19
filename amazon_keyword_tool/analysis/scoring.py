# scoring.py — A9-style composite product scoring engine

"""
Models the key signals used by Amazon's A9 search algorithm to rank products,
derived entirely from observable scraped data.

Factor weights (configurable via config.SCORE_WEIGHTS):
  - Text Relevance      (0.30): keyword match quality in title
  - Sales Velocity Proxy(0.25): log-normalised review count  → proxy for BSR
  - Customer Satisfaction(0.15): rating (sigmoid-mapped, punishes < 3.5)
  - Price Competitiveness(0.15): Gaussian distance from category median price
  - Rank Position       (0.15): observed rank in search results (ground truth)

All individual scores are in [0, 1].  The composite A9 score is also in [0, 1].
"""

import math
import logging
import re
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import numpy as np

from amazon_keyword_tool.config import SCORE_WEIGHTS

logger = logging.getLogger(__name__)


# ── Score breakdown dataclass ─────────────────────────────────────────────────

@dataclass
class ScoreBreakdown:
    """Detailed breakdown of an A9-style composite score for one product."""
    product_title:    str
    search_keyword:   str
    relevance:        float   # [0, 1]
    sales_velocity:   float   # [0, 1]
    satisfaction:     float   # [0, 1]
    price_comp:       float   # [0, 1]
    rank_position:    float   # [0, 1]
    composite:        float   # [0, 1] weighted composite

    def as_dict(self) -> dict:
        return {
            "title":            self.product_title,
            "keyword":          self.search_keyword,
            "score_relevance":  round(self.relevance, 4),
            "score_velocity":   round(self.sales_velocity, 4),
            "score_satisfaction": round(self.satisfaction, 4),
            "score_price":      round(self.price_comp, 4),
            "score_rank":       round(self.rank_position, 4),
            "a9_score":         round(self.composite, 4),
        }


# ── Individual factor scorers ─────────────────────────────────────────────────

def relevance_score(title: str, keyword: str) -> float:
    """
    Score how relevant the product title is to the search keyword.

    Rules:
      - Exact phrase match in title                     → 1.0
      - All individual words present (any order)        → 0.75
      - Majority of words present (>= 50%)              → 0.40
      - Some words present (< 50%)                      → proportional 0–0.35
      - No words present                                → 0.0

    Case-insensitive. Ignores punctuation.
    """
    if not title or not keyword:
        return 0.0

    title_clean   = re.sub(r"[^a-z0-9 ]", " ", title.lower())
    keyword_clean = re.sub(r"[^a-z0-9 ]", " ", keyword.lower()).strip()

    if not keyword_clean:
        return 0.0

    # Exact phrase match
    if keyword_clean in title_clean:
        return 1.0

    kw_words = [w for w in keyword_clean.split() if w]
    if not kw_words:
        return 0.0

    title_words = set(title_clean.split())
    matching    = [w for w in kw_words if w in title_words]
    match_ratio = len(matching) / len(kw_words)

    if match_ratio == 1.0:
        return 0.75
    elif match_ratio >= 0.5:
        return 0.40
    elif match_ratio > 0.0:
        return 0.35 * match_ratio   # proportional in [0, 0.35)
    return 0.0


def sales_velocity_score(review_count: Optional[float], max_reviews: float) -> float:
    """
    Proxy for sales velocity using review count (more reviews ≈ more sales).

    Uses log normalisation so that a product with 10k reviews doesn't
    completely dominate over one with 1k reviews.

    Args:
        review_count: raw review count (can be None/NaN)
        max_reviews:  maximum review count in the current result set

    Returns:
        Score in [0, 1]
    """
    if review_count is None or (isinstance(review_count, float) and math.isnan(review_count)):
        return 0.0
    if max_reviews <= 0:
        return 0.0

    rc = float(review_count)
    if rc <= 0:
        return 0.0

    # Log-scale normalisation
    log_rc  = math.log1p(rc)
    log_max = math.log1p(max_reviews)
    return min(log_rc / log_max, 1.0)


def satisfaction_score(rating: Optional[float]) -> float:
    """
    Map a product rating [0, 5] to a satisfaction score [0, 1].

    Uses a sigmoid-like curve that:
      - Heavily penalises ratings below 3.5 (A9 filters out low-quality products)
      - Returns ~1.0 for ratings >= 4.8
      - Returns ~0.5 for ratings around 4.0

    Formula: sigmoid((rating - 3.8) * 3)
    """
    if rating is None or (isinstance(rating, float) and math.isnan(rating)):
        return 0.25   # Neutral penalty for missing rating (benefit of the doubt)
    rating = float(rating)
    if not (0.0 <= rating <= 5.0):
        return 0.0
    # Sigmoid centred at 3.8, steepness 3
    return 1.0 / (1.0 + math.exp(-3.0 * (rating - 3.8)))


def price_competitiveness_score(
    price: Optional[float],
    median_price: float,
    std_price: float,
) -> float:
    """
    Score how price-competitive a product is relative to its category.

    Uses a Gaussian (bell-curve) centred on median_price:
      - Price exactly at median  → ~1.0
      - Price 1 std away         → ~0.61
      - Price 2 std away         → ~0.14
      - Price very far away      → ~0.0

    Both too cheap (low quality signal) and too expensive (low conversion)
    are penalised.

    Args:
        price:        product price (can be None/NaN)
        median_price: median price in the current category/result set
        std_price:    standard deviation of prices (used as bandwidth)

    Returns:
        Score in [0, 1]
    """
    if price is None or (isinstance(price, float) and math.isnan(price)):
        return 0.5   # Unknown price: neutral
    if median_price <= 0 or std_price <= 0:
        return 0.5

    price = float(price)
    z = (price - median_price) / std_price
    return math.exp(-0.5 * z * z)   # Gaussian


def rank_bonus(position: int, total: int) -> float:
    """
    Score based on observed rank position in search results.

    Position 1 → 1.0 (best), last position → approaches 0.0.
    Uses inverse-log decay so the gap between rank 1 and 5 is
    more meaningful than between rank 15 and 20.

    Args:
        position: 1-indexed rank position
        total:    total number of products in result set

    Returns:
        Score in [0, 1]
    """
    if position <= 0 or total <= 0:
        return 0.0
    if position == 1:
        return 1.0
    # Inverse log decay
    return 1.0 / math.log2(1 + position)


# ── Composite A9 scorer ───────────────────────────────────────────────────────

def composite_a9_score(
    product: dict,
    keyword: str,
    max_reviews: float,
    median_price: float,
    std_price: float,
    total_products: int,
    weights: Optional[dict] = None,
) -> ScoreBreakdown:
    """
    Compute the composite A9-style score for a single product.

    Args:
        product:        A cleaned product dict
        keyword:        The search keyword being analysed
        max_reviews:    Max review count in the result set (for normalisation)
        median_price:   Median price of the result set
        std_price:      Price standard deviation of the result set
        total_products: Total products in result set (for rank scoring)
        weights:        Optional override for SCORE_WEIGHTS

    Returns:
        ScoreBreakdown with all individual scores and composite
    """
    w = weights or SCORE_WEIGHTS

    title        = str(product.get("title", "") or "")
    review_count = product.get("review_count")
    rating       = product.get("rating")
    price        = product.get("price")
    position     = int(product.get("rank_position", total_products) or total_products)

    r = relevance_score(title, keyword)
    v = sales_velocity_score(review_count, max_reviews)
    s = satisfaction_score(rating)
    p = price_competitiveness_score(price, median_price, std_price)
    k = rank_bonus(position, total_products)

    composite = (
        w.get("relevance",      0.30) * r +
        w.get("sales_velocity", 0.25) * v +
        w.get("satisfaction",   0.15) * s +
        w.get("price_comp",     0.15) * p +
        w.get("rank_position",  0.15) * k
    )

    return ScoreBreakdown(
        product_title=title,
        search_keyword=keyword,
        relevance=r,
        sales_velocity=v,
        satisfaction=s,
        price_comp=p,
        rank_position=k,
        composite=composite,
    )


# ── Batch scorer ──────────────────────────────────────────────────────────────

def score_products(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    Score all products in a cleaned DataFrame for a given keyword.

    Adds columns: score_relevance, score_velocity, score_satisfaction,
                  score_price, score_rank, a9_score

    Args:
        df:      Cleaned products DataFrame
        keyword: Search keyword used for relevance scoring

    Returns:
        DataFrame with score columns added, sorted by a9_score descending
    """
    if df.empty:
        logger.warning("score_products: empty DataFrame.")
        return df

    # Compute category-level stats for normalisation
    max_reviews  = float(df["review_count"].max(skipna=True) or 1)
    prices       = df["price"].dropna()
    median_price = float(prices.median()) if not prices.empty else 1.0
    std_price    = float(prices.std())    if len(prices) > 1 else median_price * 0.3
    total        = len(df)

    records = df.to_dict("records")
    breakdowns = [
        composite_a9_score(
            product=r,
            keyword=keyword,
            max_reviews=max_reviews,
            median_price=median_price,
            std_price=std_price if std_price > 0 else median_price * 0.3,
            total_products=total,
        )
        for r in records
    ]

    score_df = pd.DataFrame([b.as_dict() for b in breakdowns])

    # Merge scores back into original DataFrame
    df = df.copy()
    for col in ("score_relevance", "score_velocity", "score_satisfaction",
                "score_price", "score_rank", "a9_score"):
        df[col] = score_df[col].values

    df = df.sort_values("a9_score", ascending=False).reset_index(drop=True)
    logger.info(
        f"Scored {len(df)} products for keyword={keyword!r}. "
        f"Top score: {df['a9_score'].max():.3f}"
    )
    return df
