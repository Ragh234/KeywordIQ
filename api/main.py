import asyncio
import os
import traceback
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add the project root to the path so we can import amazon_keyword_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amazon_keyword_tool.scraper.browser import scrape_amazon_search
from amazon_keyword_tool.scraper.parser import parse_search_results
from amazon_keyword_tool.analysis.data_cleaning import clean_products
from amazon_keyword_tool.analysis.keyword_research import analyze_keywords, KeywordReport
from amazon_keyword_tool.analysis.title_builder import build_title
from amazon_keyword_tool.config import SCORE_WEIGHTS

# No CORS middleware on purpose: browsers talk to the Express server, which
# calls this service server-to-server (see server/controllers/keywordController.js).
app = FastAPI(title="Amazon Keyword Tool API")

# Playwright's sync API blocks, so analyses run in worker threads.
executor = ThreadPoolExecutor(max_workers=2)

TOP_PRODUCTS_LIMIT = 20
PRODUCT_COLUMNS = [
    "title", "product_url", "price", "rating", "review_count", "rank_position",
    "a9_score", "score_relevance", "score_velocity", "score_satisfaction",
    "score_price", "score_rank",
]


class AnalyzeRequest(BaseModel):
    keyword: str
    max_pages: int = 1
    top_n: int = 20


def run_blocking_analysis(keyword: str, max_pages: int, top_n: int) -> dict:
    """Run the synchronous Playwright scraper and analysis in a thread."""
    pages = scrape_amazon_search(keyword, max_pages=max_pages)
    if not pages:
        raise ValueError(f"Scraping failed for keyword: '{keyword}'")

    all_products = []
    current_rank = 1

    for page_num, html in pages:
        products = parse_search_results(
            html=html,
            search_keyword=keyword,
            page_number=page_num,
            start_rank=current_rank
        )
        if products:
            all_products.extend(products)
            current_rank += len(products)

    if not all_products:
        raise ValueError(f"No products parsed for keyword: '{keyword}'")

    df = clean_products(all_products)
    report = analyze_keywords(df, search_keyword=keyword, top_n=top_n)
    return report_to_dict(report)


def _df_to_records(df_data: pd.DataFrame, columns: list[str] | None = None) -> list:
    """DataFrame -> list of dicts, with NaN turned into None so it is valid JSON."""
    if df_data is None or df_data.empty:
        return []
    if columns is not None:
        df_data = df_data[[c for c in columns if c in df_data.columns]]
    return df_data.astype(object).where(df_data.notna(), None).to_dict("records")


def report_to_dict(report: KeywordReport) -> dict:
    """Shape a KeywordReport into the JSON the frontend consumes."""
    top_products = _df_to_records(
        report.scored_products_df.head(TOP_PRODUCTS_LIMIT), PRODUCT_COLUMNS
    )
    suggested_title = build_title(
        report.search_keyword,
        [kw.keyword for kw in report.top_keywords],
        report.competitor_gaps,
    )

    return {
        "search_keyword": report.search_keyword,
        "total_products": report.total_products,
        "top_keywords": [
            {
                "keyword": kw.keyword,
                "importance": kw.importance,
                "frequency": kw.frequency,
                "avg_rank": kw.avg_rank,
                "tfidf_score": kw.tfidf_score,
                "rank_weighted_freq": kw.rank_weighted_freq,
            }
            for kw in report.top_keywords
        ],
        "difficulty_table": _df_to_records(report.difficulty_table),
        "price_sweet_spot": report.price_sweet_spot,
        "competitor_gaps": report.competitor_gaps,
        "title_patterns": _df_to_records(report.title_patterns),
        "top_products": top_products,
        "score_weights": SCORE_WEIGHTS,
        "suggested_title": suggested_title,
    }


@app.post("/api/analyze")
async def analyze_endpoint(req: AnalyzeRequest):
    """Trigger the keyword analysis pipeline."""
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor,
            run_blocking_analysis,
            req.keyword,
            req.max_pages,
            req.top_n,
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
