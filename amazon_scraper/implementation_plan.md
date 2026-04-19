# Amazon A9-Style Keyword Research & SEO Algorithm

Build a keyword research and product ranking algorithm inspired by Amazon's A9 search engine. It uses scraped product data (title, price, rating, review count) to reverse-engineer what makes products rank well, and outputs actionable keyword/SEO intelligence for Amazon sellers.

## User Review Required

> [!IMPORTANT]
> **Scope clarification**: This algorithm does NOT replicate the actual A9 engine (which powers Amazon's internal search). Instead, it **analyzes scraped search results** to infer ranking signals and produce keyword research insights — similar to tools like Helium10, Jungle Scout, or MerchantWords. Please confirm this matches your intent.

> [!IMPORTANT]
> **Data richness**: The current scraper only captures page-1 results for a single keyword. For meaningful keyword research, the scraper should be enhanced to:
> 1. Accept **multiple keywords** as input (or generate keyword variations automatically).
> 2. Scrape **multiple pages** of results per keyword.
> 3. Extract the **search rank position** (1st result, 2nd result, etc.).
>
> The plan below includes these enhancements. Let me know if you want to keep the scraper as-is and only build the analysis layer on top.

---

## Proposed Changes

### 1. Project Restructure

Reorganize into a clean package structure so the scraper and analysis engine live side-by-side.

#### Current structure:
```
btp/
  amazon_scraper/
    main.py, scraper.py, parser.py, config.py, utils.py
    output/products.json
```

#### Proposed structure:
```
btp/
  amazon_keyword_tool/
    __init__.py
    config.py                    # [MODIFY] unified config (scraper + analysis)
    scraper/
      __init__.py
      browser.py                 # [MOVE] from scraper.py — Playwright automation
      parser.py                  # [MOVE] from parser.py — BS4 extraction
    analysis/
      __init__.py
      data_cleaning.py           # [NEW] price normalization, N/A handling
      keyword_extractor.py       # [NEW] TF-IDF, n-gram extraction from titles
      scoring.py                 # [NEW] A9-style composite scoring engine
      keyword_research.py        # [NEW] opportunity scores, difficulty, gaps
    reporting/
      __init__.py
      console.py                 # [NEW] rich console output
      export.py                  # [MOVE+EXTEND] from utils.py — CSV/JSON/markdown
    cli.py                       # [NEW] main CLI entry point
    output/                      # scraped + analysis results
  tests/
    __init__.py
    test_data_cleaning.py        # [NEW]
    test_keyword_extractor.py    # [NEW]
    test_scoring.py              # [NEW]
    test_keyword_research.py     # [NEW]
    test_integration.py          # [NEW]
  requirements.txt               # [MODIFY] add scikit-learn, pandas, numpy
  README.md                      # [NEW]
```

> [!NOTE]
> The original `amazon_scraper/` folder will be left untouched. The new `amazon_keyword_tool/` is a fresh package that imports/adapts the scraper code.

---

### 2. Scraper Enhancements

#### [MODIFY] [config.py](file:///g:/projs/btp/amazon_keyword_tool/config.py)
- Add `SEARCH_KEYWORDS: list[str]` — support multiple keywords
- Add `MAX_PAGES: int = 3` — paginate through results
- Add `EXTRACT_RANK_POSITION: bool = True`

#### [MODIFY] [browser.py](file:///g:/projs/btp/amazon_keyword_tool/scraper/browser.py)
- Add multi-page scraping: follow "Next" pagination link
- Return a list of [(page_number, html)](file:///g:/projs/btp/amazon_scraper/main.py#14-44) tuples

#### [MODIFY] [parser.py](file:///g:/projs/btp/amazon_keyword_tool/scraper/parser.py)
- Add `rank_position` field to each product (derived from card order × page number)
- Add `search_keyword` field — tag which search query produced this result

New product schema:
```python
{
  "search_keyword": "gaming laptop",
  "rank_position": 3,
  "title": "ASUS ROG Strix G16 ...",
  "price": 89990.0,        # numeric, in base currency units
  "rating": 4.3,           # float
  "review_count": 1435,    # int
  "product_url": "https://..."
}
```

---

### 3. Data Cleaning Layer

#### [NEW] [data_cleaning.py](file:///g:/projs/btp/amazon_keyword_tool/analysis/data_cleaning.py)

| Function | Purpose |
|---|---|
| [parse_price(raw: str) -> float](file:///g:/projs/btp/amazon_scraper/parser.py#29-51) | `"₹1,54,990"` → `154990.0`; handles `$`, `€`, commas, Indian notation |
| [parse_rating(raw: str) -> float \| None](file:///g:/projs/btp/amazon_scraper/parser.py#53-78) | `"4.3"` → `4.3`; `"N/A"` → `None` |
| [parse_review_count(raw: str) -> int \| None](file:///g:/projs/btp/amazon_scraper/parser.py#80-118) | `"1,435"` → `1435`; `"N/A"` → `None` |
| `clean_product(raw: dict) -> dict` | Apply all parsers to a raw scraped product |
| `clean_products(products: list[dict]) -> pd.DataFrame` | Clean + load into pandas DataFrame |

---

### 4. Keyword Extraction Engine

#### [NEW] [keyword_extractor.py](file:///g:/projs/btp/amazon_keyword_tool/analysis/keyword_extractor.py)

Extracts meaningful keywords and phrases from product titles using:

1. **Tokenization & stopword removal** — strip brand names, filler words
2. **N-gram extraction** (unigrams, bigrams, trigrams) — e.g. "gaming laptop", "RTX 4060", "16GB RAM"
3. **TF-IDF scoring** — using scikit-learn's `TfidfVectorizer` across all titles in a search result set
4. **Keyword frequency map** — how often each keyword appears across top-ranked products

Key functions:
```python
def extract_keywords(titles: list[str], max_ngram: int = 3) -> list[KeywordInfo]
def compute_tfidf(titles: list[str]) -> dict[str, float]
def keyword_frequency_by_rank(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame
```

---

### 5. A9-Style Scoring Engine (Core Algorithm)

#### [NEW] [scoring.py](file:///g:/projs/btp/amazon_keyword_tool/analysis/scoring.py)

This is the heart of the tool. It models the key signals that Amazon's A9 algorithm uses to rank products, **derived from observable product data**.

#### Ranking Factors & Weights

| Factor | Signal | Weight | Rationale |
|---|---|---|---|
| **Text Relevance** | Keyword match in title (exact, partial, semantic) | 0.30 | A9 heavily weights title keyword relevance |
| **Sales Velocity Proxy** | [review_count](file:///g:/projs/btp/amazon_scraper/parser.py#80-118) (more reviews ≈ more sales) | 0.25 | Reviews correlate strongly with BSR |
| **Customer Satisfaction** | [rating](file:///g:/projs/btp/amazon_scraper/parser.py#53-78) (higher = better conversion) | 0.15 | A9 favors high-converting products |
| **Price Competitiveness** | Distance from category median price | 0.15 | Price affects click-through and conversion |
| **Rank Position** | Observed rank in search results | 0.15 | Ground truth from Amazon's own ranking |

#### Scoring Functions:

```python
def relevance_score(title: str, keyword: str) -> float
    """
    0.0–1.0 score based on:
    - Exact phrase match in title (1.0)
    - All words present but not as phrase (0.7)
    - Partial word overlap (proportional 0.0–0.5)
    """

def sales_velocity_score(review_count: int, max_reviews: int) -> float
    """Log-normalized review count relative to category max."""

def satisfaction_score(rating: float) -> float
    """Sigmoid-mapped rating score (ratings below 3.5 penalized heavily)."""

def price_competitiveness_score(price: float, median_price: float) -> float
    """Gaussian-like score — products near median score highest;
    outliers (too cheap = suspicious, too expensive = low conversion) score lower."""

def rank_bonus(position: int, total: int) -> float
    """Inverse rank score — position 1 gets 1.0, last position gets ~0.0."""

def composite_a9_score(product: dict, keyword: str, category_stats: dict) -> float
    """Weighted combination of all factors above."""
```

---

### 6. Keyword Research Module

#### [NEW] [keyword_research.py](file:///g:/projs/btp/amazon_keyword_tool/analysis/keyword_research.py)

Uses the scoring engine + keyword extractor to produce seller-actionable insights:

| Analysis | Output |
|---|---|
| **Keyword Opportunity Score** | For each extracted keyword: avg A9 score of products containing it, frequency, avg rank position |
| **Keyword Difficulty** | High difficulty = top products have very high review counts & ratings (hard to compete) |
| **Price Sweet Spot** | The price range where top-ranking products cluster |
| **Title Pattern Analysis** | Common word patterns in top-10 vs bottom-10 products |
| **Competitor Gap Keywords** | Keywords in top products' titles that appear in few competitor listings |

Key function:
```python
def analyze_keywords(df: pd.DataFrame, search_keyword: str) -> KeywordReport
```

Returns a `KeywordReport` dataclass with all the above.

---

### 7. CLI & Reporting

#### [NEW] [cli.py](file:///g:/projs/btp/amazon_keyword_tool/cli.py)

```
python -m amazon_keyword_tool "gaming laptop" "RTX laptop" --pages 3

# Or analyze existing scraped data:
python -m amazon_keyword_tool --input output/products.json
```

#### [NEW] [console.py](file:///g:/projs/btp/amazon_keyword_tool/reporting/console.py)
- Pretty-printed console tables (using built-in formatting, no heavy deps)
- Sections: Top Keywords, Keyword Difficulty, Price Sweet Spot, Title Recommendations

#### [MODIFY+EXTEND] [export.py](file:///g:/projs/btp/amazon_keyword_tool/reporting/export.py)
- Export keyword report to JSON, CSV, and a human-readable Markdown summary

---

## Verification Plan

### Automated Tests

All tests use **pytest** and run from the project root:

```bash
cd g:\projs\btp
pip install pytest
python -m pytest tests/ -v
```

#### 1. `tests/test_data_cleaning.py`
- Test [parse_price](file:///g:/projs/btp/amazon_scraper/parser.py#29-51) with Indian (₹1,54,990), US ($99.99), and edge cases ("N/A", empty)
- Test [parse_rating](file:///g:/projs/btp/amazon_scraper/parser.py#53-78) with valid floats, "N/A", out-of-range values
- Test [parse_review_count](file:///g:/projs/btp/amazon_scraper/parser.py#80-118) with comma-separated numbers, "N/A"
- Test `clean_product` end-to-end on a sample raw product dict

#### 2. `tests/test_keyword_extractor.py`
- Test n-gram extraction on known titles → verify expected keywords appear
- Test TF-IDF produces non-zero scores for frequent terms
- Test stopword removal (brand names, common filler)

#### 3. `tests/test_scoring.py`
- Test `relevance_score` — exact match = 1.0, no match = 0.0, partial in between
- Test `sales_velocity_score` — linear scaling, log normalization
- Test `satisfaction_score` — 5.0 → ~1.0, 2.0 → ~0.0
- Test `price_competitiveness_score` — median price → ~1.0, extreme prices → low
- Test `composite_a9_score` with mock products → verify ordering matches expectations

#### 4. `tests/test_keyword_research.py`
- Test `analyze_keywords` with sample DataFrame → verify report contains all sections
- Test keyword difficulty calculation with known data

#### 5. `tests/test_integration.py`
- Load the existing [amazon_scraper/output/products.json](file:///g:/projs/btp/amazon_scraper/output/products.json)
- Run the full pipeline (clean → extract → score → analyze)
- Assert the output report is non-empty and contains expected keys

### Manual Verification

1. **Run with existing data**: `python -m amazon_keyword_tool --input amazon_scraper/output/products.json`
   - Verify console output shows keyword table, difficulty scores, and price sweet spot
   - Verify output files are created in [output/](file:///g:/projs/btp/amazon_scraper/utils.py#23-25)

2. **Sanity check scores**: Products with high reviews + high ratings + keyword in title should score highest. Manually verify the top-3 scored products make intuitive sense.
