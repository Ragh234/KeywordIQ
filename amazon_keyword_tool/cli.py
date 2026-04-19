# cli.py — Command-line entry point for the Amazon Keyword Research Tool

"""
Usage:
    # Run with default keyword(s) from config.py
    python cli.py

    # Run with a specific keyword
    python cli.py --keyword "noise cancelling headphones"

    # Run with multiple keywords  
    python cli.py --keyword "wireless earbuds" --keyword "bluetooth speaker"

    # Load from existing JSON file (skip scraping)
    python cli.py --from-file output/products.json --keyword "wireless earbuds"

    # Skip export files
    python cli.py --no-export

    # Show more keywords in the report
    python cli.py --top-n 30
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("keyword_tool")


# ── Argument parsing ──────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="amazon-keyword-tool",
        description="Amazon A9-style keyword research tool.",
    )
    parser.add_argument(
        "--keyword", "-k",
        action="append",
        dest="keywords",
        metavar="KEYWORD",
        help="Search keyword(s) to analyse. Can be repeated. "
             "Defaults to SEARCH_KEYWORDS in config.py",
    )
    parser.add_argument(
        "--from-file", "-f",
        dest="from_file",
        metavar="FILEPATH",
        help="Load products from an existing JSON file instead of scraping. "
             "Must be used with --keyword.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Number of top keywords to include in the report (default: 20).",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Print the report to console only; do not write CSV/JSON files.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for exported files (default: output/ from config).",
    )
    parser.add_argument(
        "--no-scrape",
        action="store_true",
        help="Alias for --from-file — only run analysis, no browser automation.",
    )
    return parser.parse_args()


# ── Scraping step ──────────────────────────────────────────────────────────────

def scrape_keyword(keyword: str) -> list[dict]:
    """Scrape Amazon for a keyword and return a list of raw product dicts."""
    from amazon_keyword_tool.scraper.browser import scrape_amazon_search
    from amazon_keyword_tool.scraper.parser import parse_search_results

    logger.info(f"Scraping Amazon for: '{keyword}' …")
    
    pages = scrape_amazon_search(keyword)
    if not pages:
        logger.error(f"Scraping failed for keyword: '{keyword}'")
        return []

    all_products = []
    current_rank = 1
    
    for page_num, html in pages:
        products = parse_search_results(
            html=html, 
            search_keyword=keyword, 
            page_number=page_num, 
            start_rank=current_rank
        )
        if products:
            all_products.extend(products)
            current_rank += len(products)
        
    logger.info(f"  → {len(all_products)} raw products scraped in total across {len(pages)} pages")

    return all_products


# ── Load from file step ────────────────────────────────────────────────────────

def load_from_file(filepath: str, keyword: str) -> list[dict]:
    """Load raw products from a JSON file and inject keyword/rank metadata."""
    path = Path(filepath)
    if not path.exists():
        logger.error(f"File not found: {filepath}")
        return []

    with open(path, encoding="utf-8") as f:
        products = json.load(f)

    logger.info(f"Loaded {len(products)} products from {filepath}")

    for i, p in enumerate(products):
        if "search_keyword" not in p or not p["search_keyword"]:
            p["search_keyword"] = keyword
        if "rank_position" not in p or not p["rank_position"]:
            p["rank_position"] = i + 1

    return products


# ── Analysis pipeline ─────────────────────────────────────────────────────────

def run_analysis(products: list[dict], keyword: str, top_n: int) -> "KeywordReport":
    """Clean → analyse → return KeywordReport."""
    from amazon_keyword_tool.analysis.data_cleaning import clean_products
    from amazon_keyword_tool.analysis.keyword_research import analyze_keywords
    from amazon_keyword_tool.config import NGRAM_RANGE

    # Update per-run top-n if different from config default
    import amazon_keyword_tool.config as cfg
    cfg.TOP_KEYWORDS_N = top_n

    df     = clean_products(products)
    report = analyze_keywords(df, search_keyword=keyword)
    return report


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    from amazon_keyword_tool.config import SEARCH_KEYWORDS
    keywords = args.keywords or SEARCH_KEYWORDS

    if not keywords:
        logger.error("No keywords specified. Use --keyword or set SEARCH_KEYWORDS in config.py.")
        sys.exit(1)

    from amazon_keyword_tool.reporting.console import print_report
    from amazon_keyword_tool.reporting.export import export_all

    for keyword in keywords:
        # Step 1: Acquire raw product data
        if args.from_file:
            products = load_from_file(args.from_file, keyword)
        else:
            products = scrape_keyword(keyword)

        if not products:
            logger.warning(f"No products for keyword '{keyword}'. Skipping.")
            continue

        # Step 2: Run analysis
        report = run_analysis(products, keyword, top_n=args.top_n)

        # Step 3: Print to console
        print_report(report)

        # Step 4: Export files (unless --no-export)
        if not args.no_export:
            paths = export_all(report, directory=args.output_dir)
            logger.info("Exported files:")
            for name, path in paths.items():
                logger.info(f"  {name}: {path}")

    logger.info("Done.")


if __name__ == "__main__":
    main()
