"""Manual probe: scrape one page for a keyword and print the first 10
product titles as parsed. Requires Playwright + network access — see
tests/ for the automated (mocked) test suite.

Run from anywhere:
    python scripts/test_titles.py
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from amazon_keyword_tool.scraper.browser import scrape_amazon_search
from amazon_keyword_tool.scraper.parser import parse_search_results


def main():
    kw = "casio"
    print(f"Scraping for {kw}...")
    pages = scrape_amazon_search(kw, max_pages=1)

    if not pages:
        print("No pages scraped.")
        return

    for page_num, html in pages:
        products = parse_search_results(html=html, search_keyword=kw, page_number=page_num, start_rank=1)
        for i, p in enumerate(products[:10]):
            print(f"{i+1}. {p.title}")
        break


if __name__ == "__main__":
    main()
