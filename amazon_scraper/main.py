# main.py — Entry point: orchestrates scraping, parsing, and saving

import logging
import sys
from config import SEARCH_KEYWORD, OUTPUT_CSV, OUTPUT_JSON
from scraper import scrape_amazon_search
from parser import parse_search_results
from utils import save_to_csv, save_to_json, print_summary, setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def run(keyword: str = SEARCH_KEYWORD):
    """
    Full pipeline:
      1. Scrape Amazon search results for `keyword`
      2. Parse product cards from returned HTML
      3. Save results to CSV + JSON
      4. Print a summary to the console
    """
    print(f"\n{'='*60}")
    print(f"  Amazon Scraper")
    print(f"  Keyword : '{keyword}'")
    print(f"{'='*60}\n")

    # Step 1 — scrape
    html = scrape_amazon_search(keyword)
    if not html:
        logger.error("Scraping failed — no HTML returned. Aborting.")
        sys.exit(1)

    # Step 2 — parse
    products = parse_search_results(html)
    if not products:
        logger.warning("Parsing returned 0 products. Amazon may have changed selectors.")

    # Step 3 — save
    save_to_csv(products, OUTPUT_CSV)
    save_to_json(products, OUTPUT_JSON)

    # Step 4 — summary
    print_summary(products)


if __name__ == "__main__":
    # ─── To test a different keyword, just change SEARCH_KEYWORD in config.py ───
    # Or pass it as a command-line argument:  python main.py "gaming headset"
    if len(sys.argv) > 1:
        kw = " ".join(sys.argv[1:])
    else:
        kw = SEARCH_KEYWORD

    run(kw)
