import os
import sys

sys.path.insert(0, os.path.abspath(r"c:\Users\rmala\OneDrive\Desktop\BTP"))

from amazon_keyword_tool.scraper.browser import scrape_amazon_search
from amazon_keyword_tool.scraper.parser import parse_search_results
from amazon_keyword_tool.analysis.data_cleaning import clean_products

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
