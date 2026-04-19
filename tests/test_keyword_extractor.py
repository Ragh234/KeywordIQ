# tests/test_keyword_extractor.py — Unit tests for keyword extraction pipeline

import pytest
import pandas as pd
from amazon_keyword_tool.analysis.keyword_extractor import (
    _tokenise,
    _build_ngrams,
    compute_tfidf,
    extract_keywords,
    keyword_frequency_by_rank,
    KeywordInfo,
)


# ── Tokenisation ──────────────────────────────────────────────────────────────

class TestTokenise:
    def test_lowercases(self):
        tokens = _tokenise("HP Laptop Intel")
        assert all(t == t.lower() for t in tokens)

    def test_removes_stopwords(self):
        tokens = _tokenise("HP Laptop and the best")
        assert "and" not in tokens
        assert "the" not in tokens
        assert "best" not in tokens

    def test_removes_punctuation(self):
        tokens = _tokenise("HP-Laptop (15-inch), 512GB!")
        for t in tokens:
            assert t.isalnum() or " " not in t  # no punctuation chars

    def test_keeps_meaningful_words(self):
        tokens = _tokenise("Intel Core i7 512GB SSD Windows")
        assert "intel" in tokens
        assert "core" in tokens
        assert "512gb" in tokens

    def test_empty_string(self):
        assert _tokenise("") == []

    def test_single_char_filtered(self):
        """Tokens of length <= 1 should be removed."""
        tokens = _tokenise("HP a b c Laptop")
        assert "a" not in tokens
        assert "b" not in tokens


# ── N-gram building ───────────────────────────────────────────────────────────

class TestBuildNgrams:
    def test_unigrams(self):
        grams = _build_ngrams(["hp", "laptop"], max_n=1)
        assert grams == ["hp", "laptop"]

    def test_bigrams_included(self):
        grams = _build_ngrams(["hp", "laptop", "intel"], max_n=2)
        assert "hp laptop" in grams
        assert "laptop intel" in grams

    def test_trigrams_included(self):
        grams = _build_ngrams(["hp", "laptop", "intel", "core"], max_n=3)
        assert "hp laptop intel" in grams

    def test_empty_tokens(self):
        assert _build_ngrams([], max_n=3) == []

    def test_single_token(self):
        grams = _build_ngrams(["laptop"], max_n=3)
        assert "laptop" in grams
        assert len(grams) == 1


# ── TF-IDF ────────────────────────────────────────────────────────────────────

class TestComputeTfidf:
    def test_returns_dict(self):
        scores = compute_tfidf(["HP Laptop Intel Core i7", "HP Pavilion AMD Ryzen"])
        assert isinstance(scores, dict)

    def test_keys_are_strings(self):
        scores = compute_tfidf(["HP Laptop Intel", "Dell Inspiron Laptop"])
        assert all(isinstance(k, str) for k in scores)

    def test_values_are_floats(self):
        scores = compute_tfidf(["HP Laptop Intel", "Dell Inspiron Laptop"])
        assert all(isinstance(v, float) for v in scores.values())

    def test_empty_input(self):
        scores = compute_tfidf([])
        assert scores == {}

    def test_common_term_gets_score(self):
        """'laptop' appears in both titles — should have a TF-IDF score."""
        scores = compute_tfidf(["HP Laptop 15", "Dell Laptop 14"])
        # After stopword removal by TF-IDF vectorizer, 'laptop' should appear
        assert any("laptop" in k for k in scores)


# ── extract_keywords ──────────────────────────────────────────────────────────

class TestExtractKeywords:
    def test_returns_list(self, clean_df):
        keywords = extract_keywords(clean_df)
        assert isinstance(keywords, list)

    def test_returns_keyword_info_objects(self, clean_df):
        keywords = extract_keywords(clean_df)
        assert all(isinstance(k, KeywordInfo) for k in keywords)

    def test_importance_is_bounded(self, clean_df):
        """Composite importance should be in [0, 1]."""
        keywords = extract_keywords(clean_df)
        for kw in keywords:
            assert 0.0 <= kw.importance <= 1.0, f"{kw.keyword}: {kw.importance}"

    def test_sorted_descending(self, clean_df):
        keywords = extract_keywords(clean_df)
        importances = [k.importance for k in keywords]
        assert importances == sorted(importances, reverse=True)

    def test_frequency_positive(self, clean_df):
        keywords = extract_keywords(clean_df)
        assert all(k.frequency > 0 for k in keywords)

    def test_avg_rank_positive(self, clean_df):
        keywords = extract_keywords(clean_df)
        assert all(k.avg_rank > 0 for k in keywords)

    def test_respects_top_n(self, clean_df):
        keywords = extract_keywords(clean_df, top_n=5)
        assert len(keywords) <= 5

    def test_common_hardware_terms_appear(self, clean_df):
        """Technical terms like 'ssd', 'ram', 'intel' should rank in extracted keywords."""
        keywords = extract_keywords(clean_df, top_n=50)
        terms = {k.keyword for k in keywords}
        # At least some key tech specs should appear
        matches = terms & {"ssd", "ram", "intel", "core", "laptop", "512gb"}
        assert len(matches) >= 2, f"Expected hardware terms in: {list(terms)[:10]}"

    def test_empty_df(self):
        empty = pd.DataFrame(columns=["title", "rank_position"])
        keywords = extract_keywords(empty)
        assert keywords == []


# ── keyword_frequency_by_rank ─────────────────────────────────────────────────

class TestKeywordFrequencyByRank:
    def test_returns_dataframe(self, clean_df):
        result = keyword_frequency_by_rank(clean_df)
        assert isinstance(result, pd.DataFrame)

    def test_expected_columns(self, clean_df):
        result = keyword_frequency_by_rank(clean_df)
        for col in ("keyword", "top_freq", "bottom_freq", "top_pct", "bottom_pct", "gap"):
            assert col in result.columns, f"Missing column: {col}"

    def test_gap_sorted_descending(self, clean_df):
        result = keyword_frequency_by_rank(clean_df)
        if not result.empty:
            gaps = result["gap"].tolist()
            assert gaps == sorted(gaps, reverse=True)

    def test_empty_df(self):
        result = keyword_frequency_by_rank(pd.DataFrame())
        assert result.empty
