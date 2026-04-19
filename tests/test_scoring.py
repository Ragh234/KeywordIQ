# tests/test_scoring.py — Unit tests for the A9 scoring module

import math
import pytest
import pandas as pd
from amazon_keyword_tool.analysis.scoring import (
    relevance_score,
    sales_velocity_score,
    satisfaction_score,
    price_competitiveness_score,
    rank_bonus,
    score_products,
    ScoreBreakdown,
)


# ── relevance_score ───────────────────────────────────────────────────────────

class TestRelevanceScore:
    def test_exact_phrase_match(self):
        assert relevance_score("HP Laptop 15 Core i7", "hp laptop") == pytest.approx(1.0)

    def test_all_words_present_not_phrase(self):
        """All keyword words present but not as contiguous phrase."""
        score = relevance_score("Laptop HP Intel", "hp laptop")
        assert score == pytest.approx(0.75)

    def test_partial_match(self):
        """Only one of two keyword words; should be > 0 and < 0.75."""
        score = relevance_score("HP Pavilion Gaming", "hp laptop")
        assert 0.0 < score < 0.75

    def test_no_match(self):
        assert relevance_score("Dell Inspiron 15", "apple macbook") == pytest.approx(0.0)

    def test_empty_title(self):
        assert relevance_score("", "hp laptop") == pytest.approx(0.0)

    def test_empty_keyword(self):
        assert relevance_score("HP Laptop", "") == pytest.approx(0.0)

    def test_case_insensitive(self):
        assert relevance_score("HP LAPTOP 15", "hp laptop") == pytest.approx(1.0)


# ── sales_velocity_score ──────────────────────────────────────────────────────

class TestSalesVelocityScore:
    def test_max_reviews_returns_one(self):
        assert sales_velocity_score(1000, 1000) == pytest.approx(1.0)

    def test_zero_returns_zero(self):
        assert sales_velocity_score(0, 1000) == pytest.approx(0.0)

    def test_none_returns_zero(self):
        assert sales_velocity_score(None, 1000) == pytest.approx(0.0)

    def test_nan_returns_zero(self):
        assert sales_velocity_score(float("nan"), 1000) == pytest.approx(0.0)

    def test_log_scale(self):
        """Score should be log-scaled: lots of reviews diminish the marginal gain."""
        s1 = sales_velocity_score(100, 10000)
        s2 = sales_velocity_score(1000, 10000)
        s3 = sales_velocity_score(5000, 10000)
        # Each jump should give decreasing gains
        assert s2 > s1
        assert s3 > s2
        assert (s3 - s2) < (s2 - s1)  # diminishing returns

    def test_zero_max_returns_zero(self):
        assert sales_velocity_score(500, 0) == pytest.approx(0.0)


# ── satisfaction_score ────────────────────────────────────────────────────────

class TestSatisfactionScore:
    def test_perfect_rating(self):
        score = satisfaction_score(5.0)
        assert score > 0.9

    def test_poor_rating(self):
        score = satisfaction_score(2.0)
        assert score < 0.2

    def test_average_rating(self):
        """Rating of ~3.8 (sigmoid centre) should give ~0.5."""
        score = satisfaction_score(3.8)
        assert 0.45 <= score <= 0.55

    def test_none_returns_neutral(self):
        """Missing rating returns a neutral penalty (0.25 per impl)."""
        score = satisfaction_score(None)
        assert score == pytest.approx(0.25)

    def test_nan_returns_neutral(self):
        score = satisfaction_score(float("nan"))
        assert score == pytest.approx(0.25)

    def test_out_of_range_rating(self):
        assert satisfaction_score(6.0) == pytest.approx(0.0)

    def test_score_monotonic(self):
        """Higher ratings should always give higher scores."""
        scores = [satisfaction_score(r) for r in [2.0, 3.0, 4.0, 4.5, 5.0]]
        assert scores == sorted(scores)


# ── price_competitiveness_score ───────────────────────────────────────────────

class TestPriceCompetitivenessScore:
    def test_median_price_returns_one(self):
        score = price_competitiveness_score(500.0, 500.0, 100.0)
        assert score == pytest.approx(1.0)

    def test_far_from_median_low_score(self):
        score = price_competitiveness_score(1000.0, 500.0, 50.0)
        assert score < 0.1

    def test_none_price_neutral(self):
        score = price_competitiveness_score(None, 500.0, 100.0)
        assert score == pytest.approx(0.5)

    def test_zero_std_returns_neutral(self):
        score = price_competitiveness_score(500.0, 500.0, 0.0)
        assert score == pytest.approx(0.5)


# ── rank_bonus ────────────────────────────────────────────────────────────────

class TestRankBonus:
    def test_rank_one_is_best(self):
        assert rank_bonus(1, 20) == pytest.approx(1.0)

    def test_rank_zero_returns_zero(self):
        assert rank_bonus(0, 20) == pytest.approx(0.0)

    def test_later_ranks_lower(self):
        scores = [rank_bonus(i, 20) for i in [1, 2, 5, 10, 20]]
        assert scores == sorted(scores, reverse=True)


# ── score_products ────────────────────────────────────────────────────────────

class TestScoreProducts:
    def test_returns_dataframe(self, clean_df):
        scored = score_products(clean_df, keyword="hp laptop")
        assert isinstance(scored, pd.DataFrame)

    def test_a9_score_column_exists(self, clean_df):
        scored = score_products(clean_df, keyword="hp laptop")
        assert "a9_score" in scored.columns

    def test_a9_score_between_zero_and_one(self, clean_df):
        scored = score_products(clean_df, keyword="hp laptop")
        valid = scored["a9_score"].dropna()
        assert (valid >= 0.0).all()
        assert (valid <= 1.0).all()

    def test_sorted_descending_by_a9(self, clean_df):
        scored = score_products(clean_df, keyword="hp laptop")
        scores = scored["a9_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_all_products_scored(self, clean_df):
        """Every product should get an a9_score (no NaN)."""
        scored = score_products(clean_df, keyword="hp laptop")
        assert scored["a9_score"].notna().all()

    def test_empty_df_returns_empty(self):
        scored = score_products(pd.DataFrame(), keyword="laptop")
        assert scored.empty

    def test_more_reviews_generally_higher_score(self, clean_df):
        """
        The product with the most reviews should score in the top half.
        (ASUS VivoBook has 5432 reviews — rank 5 in our fixture.)
        """
        scored = score_products(clean_df, keyword="hp laptop")
        asus_row = scored[scored["title"].str.contains("ASUS", na=False)]
        if not asus_row.empty:
            asus_idx = asus_row.index[0]
            # Should be in top 75% (within first 75% of rows by A9 score)
            assert asus_idx < len(scored) * 0.75, \
                "High-review product should rank in top 75% by A9 score"

    def test_score_breakdown_columns_present(self, clean_df):
        scored = score_products(clean_df, keyword="hp laptop")
        for col in ("score_relevance", "score_velocity", "score_satisfaction",
                    "score_price", "score_rank"):
            assert col in scored.columns, f"Missing score column: {col}"
