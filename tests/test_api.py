"""Tests for the FastAPI analysis service (scraping is stubbed out)."""

import pytest
from fastapi.testclient import TestClient

import api.main as api_main


def _raw_products(n=24):
    """Products whose titles share several keywords; one has no price/rating."""
    products = [
        {
            "title": f"Brand{i} Wireless Earbuds Noise Cancelling Bluetooth Fast Charging Mic",
            "price": f"₹{1000 + i * 100}",
            "rating": f"{3.5 + (i % 10) / 10:.1f}",
            "review_count": str(100 + i * 50),
            "product_url": f"https://www.amazon.in/p/{i}",
            "search_keyword": "wireless earbuds",
            "page_number": 1,
            "rank_position": i + 1,
        }
        for i in range(n)
    ]
    products[3]["price"] = ""   # missing price must not break JSON encoding
    products[3]["rating"] = ""
    return products


def _client_returning(monkeypatch, products):
    monkeypatch.setattr(api_main, "scrape_amazon_search", lambda kw, max_pages=1: [(1, "<html/>")])
    monkeypatch.setattr(
        api_main, "parse_search_results", lambda html, search_keyword, page_number, start_rank: products
    )
    return TestClient(api_main.app)


@pytest.fixture
def client(monkeypatch):
    return _client_returning(monkeypatch, _raw_products())


def _analyze(client, **extra):
    return client.post("/api/analyze", json={"keyword": "wireless earbuds", **extra})


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_analyze_returns_existing_sections(client):
    body = _analyze(client).json()

    for key in ("search_keyword", "total_products", "top_keywords", "difficulty_table",
                "price_sweet_spot", "competitor_gaps", "title_patterns"):
        assert key in body
    assert body["total_products"] == 24


def test_analyze_returns_top_products_with_score_breakdown(client):
    response = _analyze(client)
    assert response.status_code == 200
    products = response.json()["top_products"]

    assert len(products) == 20  # 24 analysed, capped at the top 20
    for p in products:
        for key in ("title", "product_url", "price", "rating", "review_count", "rank_position",
                    "a9_score", "score_relevance", "score_velocity", "score_satisfaction",
                    "score_price", "score_rank"):
            assert key in p
    scores = [p["a9_score"] for p in products]
    assert scores == sorted(scores, reverse=True)


def test_missing_price_is_returned_as_null_not_nan(monkeypatch):
    # Few enough products that all of them make the top-20 cut.
    client = _client_returning(monkeypatch, _raw_products(n=10))

    response = _analyze(client)

    assert response.status_code == 200
    products = response.json()["top_products"]
    assert len(products) == 10
    assert [p["price"] for p in products].count(None) == 1


def test_analyze_returns_suggested_title(client):
    body = _analyze(client).json()
    suggestion = body["suggested_title"]

    assert suggestion["title"].startswith("Wireless Earbuds")
    assert suggestion["length"] == len(suggestion["title"]) <= suggestion["max_length"] == 200
    assert isinstance(suggestion["keywords_used"], list)


def test_top_n_is_forwarded_to_the_analysis(client):
    body = _analyze(client, top_n=3).json()

    assert len(body["top_keywords"]) == 3
    assert len(body["difficulty_table"]) == 3


def test_scrape_failure_is_a_400(monkeypatch):
    monkeypatch.setattr(api_main, "scrape_amazon_search", lambda kw, max_pages=1: [])

    response = TestClient(api_main.app).post("/api/analyze", json={"keyword": "x"})

    assert response.status_code == 400


def test_analyze_returns_score_weights_that_sum_to_one(client):
    weights = _analyze(client).json()["score_weights"]

    assert set(weights) == {"relevance", "sales_velocity", "satisfaction", "price_comp", "rank_position"}
    assert sum(weights.values()) == pytest.approx(1.0)
