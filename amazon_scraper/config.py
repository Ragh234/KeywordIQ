# config.py — All settings and CSS selectors in one place

# ── Hardcoded search keyword (change this to test different searches) ──────────
SEARCH_KEYWORD = "wireless earbuds"

# ── Amazon URLs ────────────────────────────────────────────────────────────────
AMAZON_SEARCH_URL = "https://www.amazon.in/s?k={keyword}"

# ── CSS selectors for search-results page (each product card) ─────────────────
SEARCH_SELECTORS = {
    # Each product card on the search results page
    # NOTE: data-component-type no longer present in Amazon's HTML — use data-asin
    "product_card": "div[data-asin]",

    # Within each card:
    "title":        "h2 span",                           # covers span.a-text-normal
    "price":        "span.a-price > span.a-offscreen",   # primary price
    "rating":       "span.a-icon-alt",                   # e.g. "4.5 out of 5 stars"
    # review count is extracted via aria-label on anchor tags in parser.py
}

# ── Browser / request settings ─────────────────────────────────────────────────
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

VIEWPORT = {"width": 1920, "height": 1080}

MIN_DELAY = 2   # seconds (min wait between page loads)
MAX_DELAY = 5   # seconds (max wait between page loads)
MAX_RETRIES = 3

# ── Output ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR = "output"
OUTPUT_CSV  = "output/products.csv"
OUTPUT_JSON = "output/products.json"
