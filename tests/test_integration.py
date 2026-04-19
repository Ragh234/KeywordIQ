# tests/test_integration.py — End-to-end integration test using real products.json

"""
Loads the actual products.json output from the scraper and runs the full
analysis pipeline:
    load JSON → clean → score → extract_keywords → reporting

No network calls are made; this is purely an offline integration test.
"""

import json
import os
import pytest
import pandas as pd

PRODUCTS_JSON = os.path.join(
    os.path.dirname(__file__), "..", "amazon_scraper", "output", "products.json"
)


def load_products_json():
    """Load the real products.json file, skip if missing."""
    if not os.path.exists(PRODUCTS_JSON):
        return None
    with open(PRODUCTS_JSON, encoding="utf-8") as f:
        return json.load(f)


# ── Full pipeline test ─────────────────────────────────────────────────────────

class TestFullPipeline:
    """
    End-to-end test: raw JSON → clean → score → keyword_extract.
    Skipped automatically if products.json is absent.
    """

    @pytest.fixture(scope="class")
    def products_raw(self):
        data = load_products_json()
        if not data:
            pytest.skip("products.json not found — skipping integration test")
        # Tag each product with a search_keyword and rank_position (would normally come from scraper)
        for i, p in enumerate(data):
            p.setdefault("search_keyword", "hp laptop")
            p.setdefault("rank_position", i + 1)
        return data

    @pytest.fixture(scope="class")
    def pipeline_df(self, products_raw):
        from amazon_keyword_tool.analysis.data_cleaning import clean_products
        return clean_products(products_raw)

    @pytest.fixture(scope="class")
    def scored_df(self, pipeline_df):
        from amazon_keyword_tool.analysis.scoring import score_products
        return score_products(pipeline_df, keyword="hp laptop")

    @pytest.fixture(scope="class")
    def keywords(self, pipeline_df):
        from amazon_keyword_tool.analysis.keyword_extractor import extract_keywords
        return extract_keywords(pipeline_df, top_n=20)

    # ── Cleaning phase ──────────────────────────────────────────────────────────

    def test_cleaning_produces_dataframe(self, pipeline_df):
        assert isinstance(pipeline_df, pd.DataFrame)

    def test_cleaning_not_empty(self, pipeline_df):
        assert len(pipeline_df) > 0

    def test_required_columns(self, pipeline_df):
        for col in ("title", "price", "rating", "review_count", "rank_position"):
            assert col in pipeline_df.columns

    def test_at_least_one_valid_price(self, pipeline_df):
        assert pipeline_df["price"].notna().sum() > 0

    # ── Scoring phase ───────────────────────────────────────────────────────────

    def test_a9_score_column_present(self, scored_df):
        assert "a9_score" in scored_df.columns

    def test_scores_in_range(self, scored_df):
        assert (scored_df["a9_score"] >= 0.0).all()
        assert (scored_df["a9_score"] <= 1.0).all()

    def test_dataframe_same_length_after_scoring(self, pipeline_df, scored_df):
        assert len(scored_df) == len(pipeline_df)

    def test_sorted_desc_by_a9(self, scored_df):
        scores = scored_df["a9_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    # ── Keyword extraction phase ─────────────────────────────────────────────────

    def test_keywords_returned(self, keywords):
        assert len(keywords) > 0

    def test_importance_sorted(self, keywords):
        importances = [k.importance for k in keywords]
        assert importances == sorted(importances, reverse=True)

    def test_no_stopwords_in_top_keywords(self, keywords):
        """Common stopwords like 'and', 'the', 'for' should not appear in keywords."""
        stop = {"and", "the", "for", "a", "an", "in", "of", "to", "is"}
        for kw in keywords[:10]:
            tokens = set(kw.keyword.split())
            overlap = tokens & stop
            assert not overlap, f"Stopword found in keyword: {kw.keyword!r} ({overlap})"

    def test_all_frequencies_positive(self, keywords):
        assert all(kw.frequency > 0 for kw in keywords)


# ── Fixture-based full pipeline (no file I/O) ──────────────────────────────────

class TestPipelineWithFixture:
    """Same pipeline but uses the in-memory fixture from conftest.py."""

    def test_clean_to_scored(self, clean_df):
        from amazon_keyword_tool.analysis.scoring import score_products
        scored = score_products(clean_df, keyword="hp laptop")
        assert "a9_score" in scored.columns
        assert len(scored) == len(clean_df)

    def test_keywords_non_empty(self, clean_df):
        from amazon_keyword_tool.analysis.keyword_extractor import extract_keywords
        kws = extract_keywords(clean_df, top_n=15)
        assert len(kws) > 0

    def test_full_pipeline_no_exceptions(self, raw_products):
        """Smoke test: the whole pipeline should complete without exceptions."""
        from amazon_keyword_tool.analysis.data_cleaning import clean_products
        from amazon_keyword_tool.analysis.scoring import score_products
        from amazon_keyword_tool.analysis.keyword_extractor import extract_keywords

        df = clean_products(raw_products)
        scored = score_products(df, keyword="hp laptop")
        kws = extract_keywords(df, top_n=10)

        assert not scored.empty
        assert len(kws) > 0
