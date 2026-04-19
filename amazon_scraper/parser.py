# parser.py — BeautifulSoup extraction logic for Amazon search results

import re
import logging
from bs4 import BeautifulSoup
from config import SEARCH_SELECTORS

logger = logging.getLogger(__name__)

AMAZON_BASE = "https://www.amazon.in"


def _clean_text(tag) -> str:
    """Return stripped text from a BS4 tag, or 'N/A' if tag is None."""
    return tag.get_text(strip=True) if tag else "N/A"


def _parse_title(card) -> str:
    """
    Extract product title from the h2 heading in the card.
    Amazon uses h2 > a > span or h2 > span.
    """
    h2 = card.find("h2")
    if h2:
        return h2.get_text(strip=True)
    return "N/A"


def _parse_price(card) -> str:
    """
    Extract price from the card. Amazon renders the
    accessible price inside span.a-offscreen inside span.a-price.
    Falls back to a regex hunt for dollar amounts.
    """
    # Primary selector
    tag = card.select_one("span.a-price > span.a-offscreen")
    if tag:
        return tag.get_text(strip=True)

    # Fallback: any .a-offscreen inside .a-price
    tag = card.select_one(".a-price .a-offscreen")
    if tag:
        return tag.get_text(strip=True)

    # Last resort: regex for dollar amounts in card text
    match = re.search(r"\$[\d,]+\.?\d*", card.get_text())
    if match:
        return match.group()

    return "N/A"


def _parse_rating(card) -> str:
    """
    Extract rating, e.g. '4.5 out of 5 stars' → '4.5'.
    span.a-icon-alt holds the accessible rating text.
    """
    tag = card.select_one("span.a-icon-alt")
    if tag:
        text = tag.get_text(strip=True)
        match = re.search(r"(\d+\.?\d*)\s+out\s+of", text)
        if match:
            return match.group(1)
        # Sometimes the text is just '4.5' already
        match = re.search(r"(\d+\.?\d*)", text)
        if match:
            return match.group(1)

    # Fallback: aria-label on star icon
    tag = card.select_one("i.a-icon-star, i.a-icon-star-small")
    if tag:
        label = tag.get("aria-label", "")
        match = re.search(r"(\d+\.?\d*)", label)
        if match:
            return match.group(1)

    return "N/A"


def _parse_review_count(card) -> str:
    """
    Extract total review count.
    Amazon puts the count in aria-label of the reviews anchor:
      e.g. aria-label="4.5 out of 5 stars, 12,345 ratings"
    or as a plain text span near the rating.
    """
    # Strategy 1 — aria-label on review links
    for a in card.select("a[href*='customerReviews'], a[href*='#customerReviews']"):
        label = a.get("aria-label", "")
        # pattern: "X ratings" or just a number
        match = re.search(r"([\d,]+)\s+rating", label)
        if match:
            return match.group(1).replace(",", "")

    # Strategy 2 — aria-label anywhere containing "rating"
    for tag in card.select("[aria-label]"):
        label = tag.get("aria-label", "")
        match = re.search(r"([\d,]+)\s+rating", label)
        if match:
            return match.group(1).replace(",", "")

    # Strategy 3 — span with a parenthesized count "(12,345)"
    for span in card.select("span.a-size-base"):
        txt = span.get_text(strip=True)
        match = re.match(r"^\(?(\d[\d,]*)\)?$", txt)
        if match:
            val = match.group(1).replace(",", "")
            if val.isdigit() and len(val) >= 1:
                return val

    # Strategy 4 — any digit-only span near the rating area
    for span in card.select("span.a-size-base"):
        txt = span.get_text(strip=True).replace(",", "")
        if txt.isdigit() and 2 <= len(txt) <= 8:
            return txt

    return "N/A"


def _parse_product_url(card) -> str:
    """
    Extract the full product detail URL from the card.
    Amazon search result cards use anchors with /dp/ in the href for product pages.
    """
    # Primary: any anchor whose href contains /dp/ (confirmed by HTML inspection)
    link = card.select_one("a[href*='/dp/']")
    if link and link.get("href"):
        href = link["href"]
        # Strip query string to get a clean URL
        href = href.split("?")[0]
        if href.startswith("http"):
            return href
        return AMAZON_BASE + href

    # Fallback: h2 anchor
    link = card.select_one("h2 a")
    if link and link.get("href"):
        href = link["href"]
        if href.startswith("http"):
            return href
        return AMAZON_BASE + href

    return "N/A"


def parse_search_results(html: str) -> list[dict]:
    """
    Parse the raw HTML of an Amazon search results page.

    Returns:
        List of dicts with keys: title, price, rating, review_count, product_url
    """
    soup = BeautifulSoup(html, "lxml")

    # Use div[data-asin] — the confirmed selector from real Amazon HTML
    all_cards = soup.select(SEARCH_SELECTORS["product_card"])
    # Filter out empty data-asin values (Amazon uses empty string for ads/widgets)
    cards = [c for c in all_cards if c.get("data-asin")]
    logger.info(f"Found {len(cards)} product card(s) on page.")

    products = []
    for card in cards:
        title = _parse_title(card)

        # Skip cards with no title (sponsored / ad injection cards)
        if title == "N/A" or not title:
            continue

        product = {
            "title":        title,
            "price":        _parse_price(card),
            "rating":       _parse_rating(card),
            "review_count": _parse_review_count(card),
            "product_url":  _parse_product_url(card),
        }
        products.append(product)
        logger.debug(f"  Parsed: {title[:60]}")

    return products
