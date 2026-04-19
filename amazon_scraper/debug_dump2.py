# debug_dump2.py — Waits for networkidle + more product cards

from playwright.sync_api import sync_playwright
import time, os

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

SEARCH_URL = "https://www.amazon.com/s?k=wireless+earbuds"

with sync_playwright() as pw:
    browser = pw.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    )
    ctx = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
    )
    ctx.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    page = ctx.new_page()

    # Use networkidle so JS-rendered content finishes loading
    page.goto(SEARCH_URL, wait_until="networkidle", timeout=45_000)
    time.sleep(3)

    # Scroll to trigger lazy loading
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    time.sleep(2)

    html = page.content()
    browser.close()

os.makedirs("output", exist_ok=True)
with open("output/debug_page2.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Saved {len(html):,} bytes to output/debug_page2.html")

from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")

cards_asin = [c for c in soup.select("div[data-asin]") if c.get("data-asin")]
print(f"Non-empty data-asin cards: {len(cards_asin)}")

# Try to find price and review patterns inside the first few cards
for i, card in enumerate(cards_asin[:3], 1):
    print(f"\n=== Card {i} (ASIN: {card.get('data-asin')}) ===")

    h2 = card.find("h2")
    print(f"  title  : {h2.get_text(strip=True)[:70] if h2 else 'N/A'}")

    # Price candidates
    price_candidates = [
        ("span.a-price span.a-offscreen",    card.select_one("span.a-price span.a-offscreen")),
        (".a-price .a-offscreen",            card.select_one(".a-price .a-offscreen")),
        ("span[class*='price']",             card.select_one("span[class*='price']")),
    ]
    for name, tag in price_candidates:
        if tag:
            print(f"  price ({name}): {tag.get_text(strip=True)}")
            break
    else:
        print("  price  : N/A (all selectors failed)")

    # Rating
    rating = card.select_one("span.a-icon-alt")
    print(f"  rating : {rating.get_text(strip=True) if rating else 'N/A'}")

    # Review count candidates
    rev_candidates = [
        ("#acrCustomerReviewText",                      card.select_one("#acrCustomerReviewText")),
        ("span.a-size-base.s-underline-text",           card.select_one("span.a-size-base.s-underline-text")),
        ("span.s-link-style span.a-size-base",          card.select_one("span.s-link-style span.a-size-base")),
        ("a span.a-size-base",                          None),  # loop below
    ]
    found_rev = None
    for name, tag in rev_candidates[:3]:
        if tag:
            txt = tag.get_text(strip=True).replace(",", "")
            if txt.isdigit():
                print(f"  reviews ({name}): {txt}")
                found_rev = txt
                break
    if not found_rev:
        # Brute-force: find all spans that are pure digit strings
        for span in card.select("span.a-size-base"):
            txt = span.get_text(strip=True).replace(",", "")
            if txt.isdigit() and len(txt) > 2:
                print(f"  reviews (brute-force span.a-size-base): {txt}")
                found_rev = txt
                break
    if not found_rev:
        print("  reviews: N/A")
