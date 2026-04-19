# config.py — Unified settings for scraper + analysis tool

# ── Search settings ────────────────────────────────────────────────────────────
# Default keywords to research. Pass multiple to compare categories.
SEARCH_KEYWORDS: list[str] = ["wireless earbuds"]

# Number of pages to scrape per keyword (each page ~16–20 results)
MAX_PAGES: int = 1

# ── Amazon URLs ────────────────────────────────────────────────────────────────
AMAZON_SEARCH_URL = "https://www.amazon.in/s?k={keyword}&page={page}"

# ── CSS selectors ──────────────────────────────────────────────────────────────
SEARCH_SELECTORS = {
    "product_card": "div[data-asin]",
    "title":        "h2 span",
    "price":        "span.a-price > span.a-offscreen",
    "rating":       "span.a-icon-alt",
}

# ── Browser / request settings ─────────────────────────────────────────────────
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
VIEWPORT    = {"width": 1920, "height": 1080}
MIN_DELAY   = 2
MAX_DELAY   = 5
MAX_RETRIES = 3

# ── Output ────────────────────────────────────────────────────────────────────
OUTPUT_DIR  = "output"

# ── Analysis settings ──────────────────────────────────────────────────────────
# How many top keywords to surface in the report
TOP_KEYWORDS_N: int = 20

# TF-IDF n-gram range: (1, 3) means unigrams, bigrams, trigrams
NGRAM_RANGE: tuple[int, int] = (1, 3)

# Composite score weights (must sum to 1.0)
SCORE_WEIGHTS = {
    "relevance":       0.30,
    "sales_velocity":  0.25,
    "satisfaction":    0.15,
    "price_comp":      0.15,
    "rank_position":   0.15,
}
