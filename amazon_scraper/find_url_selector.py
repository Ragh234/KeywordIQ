# find_url_selector.py — find which anchor selector works for product URLs
from bs4 import BeautifulSoup

with open("output/debug_page.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
cards = [c for c in soup.select("div[data-asin]") if c.get("data-asin")]

for i, card in enumerate(cards[:3], 1):
    print(f"--- Card {i} ---")
    # Try all anchors in h2
    for a in card.select("h2 a"):
        print(f"  h2 a href: {a.get('href', '')[:80]}")
    # Any anchor with /dp/ in href
    for a in card.select("a[href*='/dp/']"):
        print(f"  /dp/ link: {a.get('href', '')[:80]}")
        break
    print()
