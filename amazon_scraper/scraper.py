# scraper.py — Playwright browser automation

import random
import time
import logging
from playwright.sync_api import sync_playwright, Page, BrowserContext
from config import (
    AMAZON_SEARCH_URL,
    SEARCH_KEYWORD,
    USER_AGENT,
    VIEWPORT,
    MIN_DELAY,
    MAX_DELAY,
    MAX_RETRIES,
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


def scrape_amazon_search(keyword: str = SEARCH_KEYWORD) -> str | None:
    """
    Launch Playwright, navigate to the Amazon search results page
    for the given keyword, and return the raw page HTML.

    Args:
        keyword: Search term (defaults to SEARCH_KEYWORD from config.py)

    Returns:
        Raw HTML string, or None if all attempts failed.
    """
    search_url = AMAZON_SEARCH_URL.format(keyword=keyword.replace(" ", "+"))
    logger.info(f"Searching Amazon for: '{keyword}'")
    logger.info(f"URL: {search_url}")

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
        _random_delay()

        html = _get_page_html(page, search_url)

        browser.close()

    return html
