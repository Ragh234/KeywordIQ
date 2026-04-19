from bs4 import BeautifulSoup

with open("output/debug_page.html", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")

# Page title
t = soup.find("title")
print("PAGE TITLE:", t.text.strip() if t else "N/A")
print()

# Card counts
cards_asin = soup.select("div[data-asin]")
cards_comp = soup.select("div[data-component-type='s-search-result']")
print(f"div[data-asin] count            : {len(cards_asin)}")
print(f"data-component-type count       : {len(cards_comp)}")

# Title-level selectors
print(f"h2 span.a-text-normal           : {len(soup.select('h2 span.a-text-normal'))}")
print(f"h2 a span                       : {len(soup.select('h2 a span'))}")
print(f"span.a-price span.a-offscreen   : {len(soup.select('span.a-price span.a-offscreen'))}")
print(f"span.a-icon-alt                 : {len(soup.select('span.a-icon-alt'))}")
print(f"span.a-size-base.s-underline    : {len(soup.select('span.a-size-base.s-underline-text'))}")
print()

# Show structure of first card with data-asin (non-empty)
non_empty = [c for c in cards_asin if c.get("data-asin")]
print(f"Non-empty data-asin cards       : {len(non_empty)}")

if non_empty:
    c = non_empty[0]
    print()
    print("== FIRST NON-EMPTY CARD ==")
    print("data-asin:", c.get("data-asin"))
    h2 = c.find("h2")
    print("h2 text:", h2.get_text(strip=True)[:80] if h2 else "N/A")
    price = c.select_one("span.a-price span.a-offscreen")
    print("price:", price.get_text(strip=True) if price else "N/A")
    rating = c.select_one("span.a-icon-alt")
    print("rating:", rating.get_text(strip=True) if rating else "N/A")
    rev = c.select_one("span.a-size-base.s-underline-text")
    print("reviews:", rev.get_text(strip=True) if rev else "N/A")
