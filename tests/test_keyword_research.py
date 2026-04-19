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
