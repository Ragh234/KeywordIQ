# conftest.py — shared pytest fixtures

import pytest
import pandas as pd


# ── Realistic sample data mimicking Amazon scraper output ──────────────────────

SAMPLE_PRODUCTS_RAW = [
    {
        "title": "HP Laptop 15 Intel Core i7 16GB RAM 512GB SSD Windows 11",
        "price": "₹1,54,990",
        "rating": "4.3",
        "review_count": "54",
        "product_url": "https://www.amazon.in/hp-laptop/dp/B0AB1",
        "search_keyword": "hp laptop",
        "rank_position": 1,
    },
    {
        "title": "HP Pavilion Gaming Laptop AMD Ryzen 5 8GB RAM 512GB SSD",
        "price": "₹1,34,990",
        "rating": "4.1",
        "review_count": "128",
        "product_url": "https://www.amazon.in/hp-pavilion/dp/B0AB2",
        "search_keyword": "hp laptop",
        "rank_position": 2,
    },
    {
        "title": "Lenovo IdeaPad Slim 3 Intel Core i5 8GB RAM 512GB SSD Laptop",
        "price": "₹62,990",
        "rating": "4.2",
        "review_count": "2341",
        "product_url": "https://www.amazon.in/lenovo/dp/B0AB3",
        "search_keyword": "hp laptop",
        "rank_position": 3,
    },
    {
        "title": "Dell Inspiron 15 Intel Core i5 16GB RAM 1TB HDD Windows 11 Laptop",
        "price": "₹58,490",
        "rating": "4.0",
        "review_count": "876",
        "product_url": "https://www.amazon.in/dell/dp/B0AB4",
        "search_keyword": "hp laptop",
        "rank_position": 4,
    },
    {
        "title": "ASUS VivoBook 15 Intel Core i3 8GB RAM 256GB SSD",
        "price": "₹42,990",
        "rating": "4.4",
        "review_count": "5432",
        "product_url": "https://www.amazon.in/asus/dp/B0AB5",
        "search_keyword": "hp laptop",
        "rank_position": 5,
    },
    {
        "title": "Acer Aspire 5 AMD Ryzen 7 16GB RAM 512GB SSD Full HD Display",
        "price": "₹55,990",
        "rating": "4.3",
        "review_count": "3201",
        "product_url": "https://www.amazon.in/acer/dp/B0AB6",
        "search_keyword": "hp laptop",
        "rank_position": 6,
    },
    {
        "title": "HP 15s Intel Core i5 8GB RAM 512GB SSD Fresh Windows 11",
        "price": "₹69,990",
        "rating": "4.5",
        "review_count": "1203",
        "product_url": "https://www.amazon.in/hp-15s/dp/B0AB7",
        "search_keyword": "hp laptop",
        "rank_position": 7,
    },
    {
        "title": "MSI Modern 14 Intel Core i7 16GB RAM 512GB SSD Laptop",
        "price": "₹89,990",
        "rating": "N/A",
        "review_count": "N/A",
        "product_url": "N/A",
        "search_keyword": "hp laptop",
        "rank_position": 8,
    },
]


@pytest.fixture
def raw_products():
    """Return list of raw product dicts as they come from the scraper."""
    return list(SAMPLE_PRODUCTS_RAW)


@pytest.fixture
def clean_df(raw_products):
    """Return a cleaned DataFrame ready for analysis."""
    from amazon_keyword_tool.analysis.data_cleaning import clean_products
    return clean_products(raw_products)


@pytest.fixture
def scored_df(clean_df):
    """Return a scored DataFrame with a9_score column."""
    from amazon_keyword_tool.analysis.scoring import score_products
    return score_products(clean_df, keyword="hp laptop")
