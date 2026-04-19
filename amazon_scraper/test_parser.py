# test_parser.py — Test parser against saved HTML without running Playwright
import sys
sys.path.insert(0, ".")

from parser import parse_search_results
from utils import print_summary, save_to_csv, save_to_json

if __name__ == "__main__":
    with open("output/debug_page.html", encoding="utf-8") as f:
        html = f.read()

    products = parse_search_results(html)
    print(f"\nParsed {len(products)} products from saved HTML\n")

    print_summary(products[:5])  # show first 5

    # Save full results
    save_to_csv(products, "output/products.csv")
    save_to_json(products, "output/products.json")
