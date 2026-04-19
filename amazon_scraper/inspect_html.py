# inspect_html.py - Find correct selectors from saved HTML

from bs4 import BeautifulSoup
import re

with open("output/debug_page.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Get all real product cards (non-empty data-asin)
cards = [c for c in soup.select("div[data-asin]") if c.get("data-asin")]
print(f"Total product cards: {len(cards)}")
print()

# Examine first 5 cards in detail
for i, card in enumerate(cards[:5], 1):
    asin = card.get("data-asin")
    print(f"--- Card {i}: ASIN={asin} ---")

    # TITLE
    h2 = card.find("h2")
    if h2:
        print(f"  Title: {h2.get_text(strip=True)[:70]}")

    # PRICE — try several selectors
    price_found = False
    for sel in [
        "span.a-price > span.a-offscreen",
        ".a-price .a-offscreen",
        "span[class='a-offscreen']",
    ]:
        tag = card.select_one(sel)
        if tag:
            print(f"  Price ({sel}): {tag.get_text(strip=True)}")
            price_found = True
            break
    if not price_found:
        # Hunt for any dollar amount in the card text
        match = re.search(r"\$[\d,]+\.?\d*", card.get_text())
        if match:
            print(f"  Price (regex): {match.group()}")
        else:
            print("  Price: N/A")

    # RATING
    for sel in ["span.a-icon-alt", "i.a-icon-star span", "span[aria-label*='stars']"]:
        tag = card.select_one(sel)
        if tag:
            text = tag.get_text(strip=True) or tag.get("aria-label", "")
            match = re.search(r"(\d+\.?\d*)", text)
            if match:
                print(f"  Rating ({sel}): {match.group(1)}")
                break

    # REVIEW COUNT — hunt for digit-only spans near rating
    rev_found = False
    for sel in [
        "span.a-size-base.s-underline-text",
        "span.s-link-style.a-text-normal span",
        "span.a-size-base",
    ]:
        for tag in card.select(sel):
            txt = tag.get_text(strip=True).replace(",", "").replace("(", "").replace(")", "")
            if txt.isdigit() and len(txt) > 1:
                print(f"  Reviews ({sel}): {txt}")
                rev_found = True
                break
        if rev_found:
            break
    if not rev_found:
        # Try aria-label on review links
        for a in card.select("a[href*='customerReviews'], a[href*='reviews']"):
            lab = a.get("aria-label", "")
            match = re.search(r"([\d,]+)", lab)
            if match:
                print(f"  Reviews (aria-label): {match.group(1).replace(',','')}")
                rev_found = True
                break
    if not rev_found:
        print("  Reviews: N/A")

    print()
