# utils.py — CSV/JSON saving and logging helpers

import csv
import json
import logging
import os
from config import OUTPUT_DIR


def setup_logging():
    """Configure console + optional file logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_to_csv(products: list[dict], filepath: str):
    """Save list of product dicts to a CSV file."""
    ensure_output_dir()
    if not products:
        logger.warning("No products to save to CSV.")
        return
    fieldnames = ["title", "price", "rating", "review_count", "product_url"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)
    logger.info(f"CSV saved → {filepath} ({len(products)} records)")


def save_to_json(products: list[dict], filepath: str):
    """Save list of product dicts to a pretty-printed JSON file."""
    ensure_output_dir()
    if not products:
        logger.warning("No products to save to JSON.")
        return
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    logger.info(f"JSON saved → {filepath} ({len(products)} records)")


def print_summary(products: list[dict]):
    """Print a quick table of scraped results to the console."""
    if not products:
        print("\n[!] No products were scraped.\n")
        return

    print(f"\n{'='*80}")
    print(f"  Scraped {len(products)} product(s)")
    print(f"{'='*80}")
    for i, p in enumerate(products, 1):
        print(f"\n  [{i}] {p.get('title', 'N/A')[:70]}")
        print(f"       Price        : {p.get('price', 'N/A')}")
        print(f"       Rating       : {p.get('rating', 'N/A')}")
        print(f"       Review Count : {p.get('review_count', 'N/A')}")
    print(f"\n{'='*80}\n")
