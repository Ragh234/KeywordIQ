import os
import sys

sys.path.insert(0, os.path.abspath(r"c:\Users\rmala\OneDrive\Desktop\BTP"))

from amazon_keyword_tool.scraper.browser import scrape_amazon_search
from amazon_keyword_tool.scraper.parser import parse_search_results
from amazon_keyword_tool.analysis.data_cleaning import clean_products
from amazon_keyword_tool.analysis.keyword_research import analyze_keywords

def main():
    kw = "casio"
    print(f"Scraping for {kw}...")
    pages = scrape_amazon_search(kw, max_pages=1)
    
    all_products = []
    current_rank = 1
    for page_num, html in pages:
        products = parse_search_results(html=html, search_keyword=kw, page_number=page_num, start_rank=current_rank)
        if products:
            all_products.extend(products)
            current_rank += len(products)
            
    print(f"Parsed {len(all_products)} products.")
    df = clean_products(all_products)
    print(f"Cleaned {len(df)} products.")
    
    report = analyze_keywords(df, search_keyword=kw)
    print("--- TOP KEYWORDS ---")
    for k in report.top_keywords:
        print(f"{k.keyword}: freq={k.frequency}, tfidf={k.tfidf_score:.3f}, rank={k.avg_rank:.1f}, imp={k.importance:.3f}")
        
    print("--- FREQUENCIES (if any were filtered out) ---")
    from amazon_keyword_tool.analysis.keyword_extractor import _tokenise, _build_ngrams
    from collections import Counter
    counts = Counter()
    for t in df["title"].dropna():
        tokens = _tokenise(str(t))
        counts.update(set(_build_ngrams(tokens, 3)))
    print(counts.most_common(20))

if __name__ == "__main__":
    main()
