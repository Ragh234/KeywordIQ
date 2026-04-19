# data_cleaning.py — Normalize raw scraped strings into typed values

"""
Converts the raw string fields produced by the Amazon scraper into
properly typed Python values suitable for analysis.

Raw format example (from products.json):
    {
        "title": "HP Laptop 15",
        "price": "₹1,54,990",
        "rating": "4.3",
        "review_count": "1435",
        "product_url": "https://www.amazon.in/..."
    }

Cleaned format:
    {
        "title": "HP Laptop 15",
        "price": 154990.0,       # float; None if unparseable
        "rating": 4.3,           # float; None if unparseable
        "review_count": 1435,    # int;   None if unparseable
        "product_url": "https://...",
        "search_keyword": "wireless earbuds",  # injected by caller
        "rank_position": 1,                    # injected by caller
    }
"""

import re
import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


# ── Individual field parsers ───────────────────────────────────────────────────

def parse_price(raw: str) -> Optional[float]:
    """
    Parse a price string into a float.

    Handles:
      - Indian Rupee notation: ₹1,54,990  → 154990.0
      - Dollar/Euro notation:  $1,299.99  → 1299.99
      - Plain numbers:         29999      → 29999.0
      - "N/A" or empty        → None
    """
    if not raw or str(raw).strip().upper() in ("N/A", "NONE", ""):
        return None
    # Remove currency symbols and whitespace
    cleaned = re.sub(r"[₹$€£¥\s]", "", str(raw))
    # Remove all commas (handles both Indian and Western notation)
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        logger.debug(f"Could not parse price: {raw!r}")
        return None


def parse_rating(raw: str) -> Optional[float]:
    """
    Parse a rating string into a float between 0 and 5.

    Handles:
      - "4.3"             → 4.3
      - "4.3 out of 5"   → 4.3
      - "N/A"             → None
    """
    if not raw or str(raw).strip().upper() in ("N/A", "NONE", ""):
        return None
    match = re.search(r"(\d+\.?\d*)", str(raw))
    if match:
        val = float(match.group(1))
        if 0.0 <= val <= 5.0:
            return val
        logger.debug(f"Rating out of range [0,5]: {raw!r}")
    return None


def parse_review_count(raw: str) -> Optional[int]:
    """
    Parse a review count string into an integer.

    Handles:
      - "1,435"   → 1435
      - "12345"   → 12345
      - "N/A"     → None
    """
    if not raw or str(raw).strip().upper() in ("N/A", "NONE", ""):
        return None
    cleaned = str(raw).replace(",", "").strip()
    if cleaned.isdigit():
        return int(cleaned)
    # Try extracting any leading digits
    match = re.match(r"^(\d+)", cleaned)
    if match:
        return int(match.group(1))
    logger.debug(f"Could not parse review_count: {raw!r}")
    return None


def parse_title(raw: str) -> str:
    """Clean and return the product title string."""
    if not raw or str(raw).strip().upper() in ("N/A", "NONE", ""):
        return ""
    return str(raw).strip()


# ── Product-level cleaner ──────────────────────────────────────────────────────

def clean_product(raw: dict) -> dict:
    """
    Apply all field parsers to a single raw product dict.

    Args:
        raw: product dict with string fields as scraped from Amazon

    Returns:
        A new dict with typed/cleaned fields. Unknown fields are passed through.
    """
    cleaned = dict(raw)  # preserve any extra fields (search_keyword, rank_position, etc.)
    cleaned["title"]        = parse_title(raw.get("title", ""))
    cleaned["price"]        = parse_price(raw.get("price", ""))
    cleaned["rating"]       = parse_rating(raw.get("rating", ""))
    cleaned["review_count"] = parse_review_count(raw.get("review_count", ""))
    return cleaned


# ── Batch cleaner → DataFrame ──────────────────────────────────────────────────

def clean_products(products: list[dict]) -> pd.DataFrame:
    """
    Clean a list of raw product dicts and load into a pandas DataFrame.

    Missing numeric fields become NaN (standard pandas behaviour).

    Args:
        products: list of raw product dicts from the scraper

    Returns:
        DataFrame with columns: title, price, rating, review_count,
                                product_url, search_keyword (if present),
                                rank_position (if present)
    """
    if not products:
        logger.warning("clean_products: received empty product list.")
        return pd.DataFrame()

    cleaned = [clean_product(p) for p in products]

    df = pd.DataFrame(cleaned)

    # Ensure expected columns exist even if some products are missing them
    for col in ("title", "price", "rating", "review_count", "product_url"):
        if col not in df.columns:
            df[col] = None

    # Add rank_position if not already present (0-indexed in scraper, make 1-indexed)
    if "rank_position" not in df.columns:
        df["rank_position"] = range(1, len(df) + 1)

    if "search_keyword" not in df.columns:
        df["search_keyword"] = ""

    logger.info(
        f"Cleaned {len(df)} products. "
        f"Price: {df['price'].notna().sum()} valid, "
        f"Rating: {df['rating'].notna().sum()} valid, "
        f"Reviews: {df['review_count'].notna().sum()} valid."
    )
    return df
