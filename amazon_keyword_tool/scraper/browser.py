# browser.py — Playwright browser automation

import random
import time
import logging
from playwright.sync_api import sync_playwright, Page, BrowserContext
from amazon_keyword_tool.config import (
    AMAZON_SEARCH_URL,
    USER_AGENT,
    VIEWPORT,
    MIN_DELAY,
    MAX_DELAY,
    MAX_RETRIES,
    MAX_PAGES,
)

logger = logging.getLogger(__name__)


def _random_delay():
    """Sleep for a random duration to mimic human browsing."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    logger.debug(f"  Waiting {delay:.1f}s ...")
    time.sleep(delay)


def _is_captcha_page(html: str) -> bool:
    """Detect if Amazon returned a robot/CAPTCHA page."""
    markers = [
        "Enter the characters you see below",
        "Sorry, we just need to make sure you're not a robot",
        "Type the characters you see in this image",
        "api-services-support@amazon.com",
    ]
    return any(m.lower() in html.lower() for m in markers)


def _get_page_html(page: Page, url: str) -> str | None:
    """
    Navigate to a URL and return the page HTML.
    Retries up to MAX_RETRIES times on CAPTCHA or network errors.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"  → Loading (attempt {attempt}): {url[:80]}")
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)

            # Wait for search results or product title to appear
            try:
                page.wait_for_selector(
                    "div[data-component-type='s-search-result'], #productTitle",
                    timeout=10_000,
                )
            except Exception:
                logger.warning("  Selector not found — page may have changed or CAPTCHA appeared.")

            html = page.content()

            if _is_captcha_page(html):
                logger.warning(f"  CAPTCHA detected on attempt {attempt}. Waiting 10s ...")
                time.sleep(10)
                continue

            return html

        except Exception as e:
            logger.error(f"  Error on attempt {attempt}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(5)

    logger.error(f"  Failed to load after {MAX_RETRIES} attempts: {url}")
    return None


def scrape_amazon_search(keyword: str, max_pages: int = None) -> list[tuple[int, str]]:
    """
    Launch Playwright, navigate to the Amazon search results page
    for the given keyword, and return the raw page HTMLs for multiple pages.

    Args:
        keyword: Search term
        max_pages: Number of pages to scrape (defaults to MAX_PAGES from config.py)

    Returns:
        List of tuples (page_number, html_string).
    """
    if max_pages is None:
        max_pages = MAX_PAGES

    logger.info(f"Searching Amazon for: '{keyword}' (up to {max_pages} pages)")
    
    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context: BrowserContext = browser.new_context(
            user_agent=USER_AGENT,
            viewport=VIEWPORT,
            locale="en-US",
            timezone_id="America/New_York",
        )

        # Remove the 'navigator.webdriver' property to avoid bot detection
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        page = context.new_page()
        
        for page_num in range(1, max_pages + 1):
            search_url = AMAZON_SEARCH_URL.format(keyword=keyword.replace(" ", "+"), page=page_num)
            _random_delay()

            html = _get_page_html(page, search_url)
            if not html:
                break
                
            results.append((page_num, html))
            
            # Check if there is a next page
            try:
                next_btn = page.query_selector("a.s-pagination-next")
                if not next_btn:
                    logger.info("  No more pages found.")
                    break
                
                class_attr = next_btn.getAttribute("class") or ""
                href_attr = next_btn.getAttribute("href") or ""
                
                if "a-disabled" in class_attr or "" == href_attr:
                    logger.info("  No more pages found (button disabled).")
                    break
            except Exception as e:
                logger.debug(f"  Error checking pagination: {e}")
                break

        browser.close()

    return results
