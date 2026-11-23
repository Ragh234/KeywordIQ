import pandas as pd
from amazon_keyword_tool.analysis.keyword_research import (
    analyze_keywords,
    _keyword_difficulty,
    _price_sweet_spot,
    KeywordReport,
)

def test_analyze_keywords(clean_df):
    report = analyze_keywords(clean_df, search_keyword="hp laptop")
    
    assert isinstance(report, KeywordReport)
    assert report.search_keyword == "hp laptop"
    assert report.total_products == len(clean_df)
    assert not report.scored_products_df.empty
    
    assert isinstance(report.top_keywords, list)
    assert len(report.top_keywords) > 0
    
    assert not report.difficulty_table.empty
    assert "keyword" in report.difficulty_table.columns
    assert "difficulty" in report.difficulty_table.columns
    
    assert isinstance(report.price_sweet_spot, dict)
    assert "low" in report.price_sweet_spot
    assert "high" in report.price_sweet_spot
    assert "median" in report.price_sweet_spot
    assert "mean" in report.price_sweet_spot


def test_keyword_difficulty(scored_df):
    # Test with empty DataFrame
    empty_df = pd.DataFrame(columns=scored_df.columns)
    diff_empty = _keyword_difficulty(empty_df)
    assert diff_empty == 0.0

    # Test with the sample scored DataFrame
    diff = _keyword_difficulty(scored_df)
    assert isinstance(diff, float)
    assert 0.0 <= diff <= 100.0


def test_price_sweet_spot(scored_df):
    spot = _price_sweet_spot(scored_df, top_n_rank=5)
    
    assert isinstance(spot, dict)
    assert spot["low"] <= spot["high"]
    assert "median" in spot
    assert "mean" in spot
    assert "note" in spot


# ── Regression: multi-word keywords used to report 0 products ────────────────

def _earbud_df(n=12):
    """Products whose titles all contain the two-word phrase 'noise cancelling'."""
    from amazon_keyword_tool.analysis.data_cleaning import clean_products

    raw = [
        {
            "title": f"Brand{i} Wireless Earbuds Noise Cancelling Bluetooth 5.3 with Mic",
            "price": f"₹{1000 + i * 100}",
            "rating": "4.2",
            "review_count": str(100 + i * 50),
            "product_url": f"https://www.amazon.in/p/{i}",
            "search_keyword": "wireless earbuds",
            "rank_position": i + 1,
        }
        for i in range(n)
    ]
    return clean_products(raw)


def test_multiword_keyword_counts_products_that_contain_it():
    report = analyze_keywords(_earbud_df(), search_keyword="wireless earbuds")
    table = report.difficulty_table.set_index("keyword")

    assert "noise cancelling" in table.index
    assert table.loc["noise cancelling", "product_count"] == 12
    assert table.loc["noise cancelling", "difficulty"] > 0


def test_every_extracted_keyword_matches_at_least_one_product():
    report = analyze_keywords(_earbud_df(), search_keyword="wireless earbuds")

    assert (report.difficulty_table["product_count"] > 0).all()
    # A keyword's product count must agree with how often it was extracted.
    freq = {k.keyword: k.frequency for k in report.top_keywords}
    for _, row in report.difficulty_table.iterrows():
        assert row["product_count"] == freq[row["keyword"]]


# ── top_n is honoured instead of silently using the config default ───────────

def test_top_n_limits_number_of_keywords():
    report = analyze_keywords(_earbud_df(), search_keyword="wireless earbuds", top_n=5)

    assert len(report.top_keywords) == 5
    assert len(report.difficulty_table) == 5


def test_top_n_defaults_to_config_value():
    from amazon_keyword_tool.config import TOP_KEYWORDS_N

    report = analyze_keywords(_earbud_df(), search_keyword="wireless earbuds")

    assert len(report.top_keywords) <= TOP_KEYWORDS_N
