# tests/test_data_cleaning.py — Unit tests for data_cleaning module

import pytest
import pandas as pd
from amazon_keyword_tool.analysis.data_cleaning import (
    parse_price,
    parse_rating,
    parse_review_count,
    parse_title,
    clean_product,
    clean_products,
)


# ── parse_price ───────────────────────────────────────────────────────────────

class TestParsePrice:
    def test_indian_rupee_format(self):
        assert parse_price("₹1,54,990") == 154990.0

    def test_western_dollar_format(self):
        assert parse_price("$1,299.99") == 1299.99

    def test_plain_number(self):
        assert parse_price("29999") == 29999.0

    def test_na_returns_none(self):
        assert parse_price("N/A") is None

    def test_empty_returns_none(self):
        assert parse_price("") is None

    def test_none_returns_none(self):
        assert parse_price(None) is None

    def test_with_spaces(self):
        assert parse_price("₹ 62,990") == 62990.0

    def test_rupee_without_commas(self):
        assert parse_price("₹58490") == 58490.0


# ── parse_rating ──────────────────────────────────────────────────────────────

class TestParseRating:
    def test_plain_float(self):
        assert parse_rating("4.3") == 4.3

    def test_out_of_5_format(self):
        assert parse_rating("4.3 out of 5") == 4.3

    def test_integer_rating(self):
        assert parse_rating("5") == 5.0

    def test_na_returns_none(self):
        assert parse_rating("N/A") is None

    def test_out_of_range_returns_none(self):
        assert parse_rating("6.0") is None

    def test_empty_returns_none(self):
        assert parse_rating("") is None

    def test_zero_rating(self):
        assert parse_rating("0") == 0.0


# ── parse_review_count ────────────────────────────────────────────────────────

class TestParseReviewCount:
    def test_simple_integer(self):
        assert parse_review_count("1435") == 1435

    def test_comma_separated(self):
        assert parse_review_count("1,435") == 1435

    def test_large_number(self):
        assert parse_review_count("12,345") == 12345

    def test_na_returns_none(self):
        assert parse_review_count("N/A") is None

    def test_empty_returns_none(self):
        assert parse_review_count("") is None

    def test_single_digit(self):
        assert parse_review_count("1") == 1


# ── parse_title ───────────────────────────────────────────────────────────────

class TestParseTitle:
    def test_normal_title(self):
        assert parse_title("HP Laptop 15") == "HP Laptop 15"

    def test_strips_whitespace(self):
        assert parse_title("  HP Laptop  ") == "HP Laptop"

    def test_na_returns_empty(self):
        assert parse_title("N/A") == ""

    def test_empty_returns_empty(self):
        assert parse_title("") == ""


# ── clean_product ─────────────────────────────────────────────────────────────

class TestCleanProduct:
    def test_full_product(self):
        raw = {
            "title": "HP Laptop 15",
            "price": "₹1,54,990",
            "rating": "4.3",
            "review_count": "54",
            "product_url": "https://amazon.in/dp/B0001",
            "rank_position": 1,
            "search_keyword": "hp laptop",
        }
        cleaned = clean_product(raw)
        assert cleaned["title"] == "HP Laptop 15"
        assert cleaned["price"] == 154990.0
        assert cleaned["rating"] == 4.3
        assert cleaned["review_count"] == 54
        # Extra fields preserved
        assert cleaned["product_url"] == "https://amazon.in/dp/B0001"
        assert cleaned["rank_position"] == 1

    def test_na_fields_become_none(self):
        raw = {"title": "HP", "price": "N/A", "rating": "N/A", "review_count": "N/A"}
        cleaned = clean_product(raw)
        assert cleaned["price"] is None
        assert cleaned["rating"] is None
        assert cleaned["review_count"] is None


# ── clean_products → DataFrame ────────────────────────────────────────────────

class TestCleanProducts:
    def test_returns_dataframe(self, raw_products):
        df = clean_products(raw_products)
        assert isinstance(df, pd.DataFrame)

    def test_row_count(self, raw_products):
        df = clean_products(raw_products)
        assert len(df) == len(raw_products)

    def test_expected_columns(self, raw_products):
        df = clean_products(raw_products)
        for col in ("title", "price", "rating", "review_count", "rank_position"):
            assert col in df.columns, f"Missing column: {col}"

    def test_price_is_float(self, raw_products):
        df = clean_products(raw_products)
        valid = df["price"].dropna()
        assert all(isinstance(v, float) for v in valid)

    def test_rating_is_float(self, raw_products):
        df = clean_products(raw_products)
        valid = df["rating"].dropna()
        assert all(isinstance(v, float) for v in valid)

    def test_review_count_valid(self, raw_products):
        df = clean_products(raw_products)
        valid = df["review_count"].dropna()
        assert len(valid) > 0
        assert all(v > 0 for v in valid)

    def test_empty_input_returns_empty_df(self):
        df = clean_products([])
        assert df.empty

    def test_na_rating_is_nan(self, raw_products):
        """MSI product (rank 8) has N/A rating → should be NaN."""
        df = clean_products(raw_products)
        msi_row = df[df["title"].str.contains("MSI", na=False)]
        assert not msi_row.empty
        assert pd.isna(msi_row.iloc[0]["rating"])

    def test_rank_position_auto_assigned_when_missing(self):
        """If rank_position not in raw data, it should be auto-assigned 1..N."""
        products = [
            {"title": "Product A", "price": "₹10,000", "rating": "4.0", "review_count": "100"},
            {"title": "Product B", "price": "₹20,000", "rating": "4.5", "review_count": "200"},
        ]
        df = clean_products(products)
        assert list(df["rank_position"]) == [1, 2]
