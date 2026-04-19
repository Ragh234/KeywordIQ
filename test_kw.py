import os
import sys
import json
import pandas as pd
from pprint import pprint

sys.path.insert(0, os.path.abspath(r"c:\Users\rmala\OneDrive\Desktop\BTP"))

from amazon_keyword_tool.analysis.keyword_extractor import extract_keywords
from amazon_keyword_tool.analysis.keyword_research import analyze_keywords

def main():
    output_dir = r"c:\Users\rmala\OneDrive\Desktop\BTP\output"
    files = [f for f in os.listdir(output_dir) if f.startswith("report_") and f.endswith(".json")]
    files.sort(reverse=True)
    if not files:
        print("No reports found.")
        return
        
    latest_report = os.path.join(output_dir, files[0])
    print(f"Loading {latest_report}...")
    
    with open(latest_report, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # extract the "scored_products_df" from previous logic if we can, 
    # but the JSON only has the final report. We need raw products.
    # Fortunately the report_xxx.json doesn't contain raw products!
    
    # We can fetch the raw Amazon products from tests or we can just mock it.
    # Wait, the JSON report contains "search_keyword", "total_products", etc.
    print(f"Metadata: {data.get('metadata')}")
    print("Top keywords in file:")
    for kw in data.get("top_keywords", [])[:10]:
        print(f"  - {kw['keyword']}: freq={kw['frequency']}, imp={kw['importance']}")

if __name__ == "__main__":
    main()
