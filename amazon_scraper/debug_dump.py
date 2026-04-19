# debug_dump.py — Saves raw HTML to disk for selector inspection

from playwright.sync_api import sync_playwright
import os

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
    page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=30_000)
    import time; time.sleep(3)
    html = page.content()
    browser.close()

os.makedirs("output", exist_ok=True)
with open("output/debug_page.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Saved {len(html)} bytes to output/debug_page.html")

# Quick sniff: check which selectors are present
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")

selectors_to_test = {
    "product_card_old":  "div[data-component-type='s-search-result']",
    "product_card_new":  "div.s-result-item[data-asin]",
    "title_h2_span":     "h2 span.a-text-normal",
    "title_h2_a":        "h2 a span",
    "price_offscreen":   "span.a-price span.a-offscreen",
    "rating_alt":        "span.a-icon-alt",
    "reviews_underline": "span.a-size-base.s-underline-text",
    "reviews_count_cls": "span[aria-label*='stars']",
}

print("\nSelector presence on page:")
for name, sel in selectors_to_test.items():
    count = len(soup.select(sel))
    print(f"  {name:30s} → {count} match(es)")
