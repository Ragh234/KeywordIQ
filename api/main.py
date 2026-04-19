import os
import sys
import json
import glob
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the project root to the path so we can import amazon_keyword_tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amazon_keyword_tool.scraper.browser import scrape_amazon_search
from amazon_keyword_tool.scraper.parser import parse_search_results
from amazon_keyword_tool.analysis.data_cleaning import clean_products
from amazon_keyword_tool.analysis.keyword_research import analyze_keywords
from amazon_keyword_tool.config import SEARCH_KEYWORDS

app = FastAPI(title="Amazon Keyword Tool API")

# Configure CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all. Change in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=2)

# ── Output directory (relative to project root) ──
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))


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
    report = analyze_keywords(df, search_keyword=keyword)

    # Convert report to dict — include title_patterns
    import pandas as pd

    def _df_to_records(df_data: pd.DataFrame) -> list:
        if df_data is None or df_data.empty:
            return []
        return df_data.where(df_data.notna(), None).to_dict("records")

    return {
        "search_keyword": report.search_keyword,
        "total_products": report.total_products,
        "top_keywords": [
            {
                "keyword": kw.keyword,
                "importance": kw.importance,
                "frequency": kw.frequency,
                "avg_rank": kw.avg_rank,
                "tfidf_score": getattr(kw, "tfidf_score", 0),
                "rank_weighted_freq": getattr(kw, "rank_weighted_freq", 0),
            }
            for kw in report.top_keywords
        ],
        "difficulty_table": report.difficulty_table.to_dict(orient="records")
        if not report.difficulty_table.empty
        else [],
        "price_sweet_spot": report.price_sweet_spot,
        "competitor_gaps": report.competitor_gaps,
        "title_patterns": _df_to_records(report.title_patterns),
    }


@app.post("/api/analyze")
async def analyze_endpoint(req: AnalyzeRequest):
    """Trigger the keyword analysis pipeline."""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/api/reports")
def list_reports():
    """List all saved JSON reports from the output directory."""
    reports = []
    pattern = os.path.join(OUTPUT_DIR, "report_*.json")
    files = sorted(glob.glob(pattern), reverse=True)  # newest first

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            top_keywords = data.get("top_keywords", [])
            top_kw = top_keywords[0]["keyword"] if top_keywords else None

            # Use filename (without extension) as ID
            report_id = os.path.splitext(os.path.basename(filepath))[0]

            reports.append(
                {
                    "id": report_id,
                    "search_keyword": metadata.get("search_keyword", "unknown"),
                    "total_products": metadata.get("total_products", 0),
                    "generated_at": metadata.get("generated_at", ""),
                    "top_keyword": top_kw,
                }
            )
        except Exception:
            continue  # skip malformed files

    return reports


@app.get("/api/reports/{report_id}")
def get_report(report_id: str):
    """Return the full JSON content of a specific saved report."""
    # Sanitize report_id to prevent path traversal
    safe_id = os.path.basename(report_id)
    filepath = os.path.join(OUTPUT_DIR, f"{safe_id}.json")

    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Flatten for frontend consumption (match analyze endpoint shape)
        metadata = data.get("metadata", {})
        return {
            "search_keyword": metadata.get("search_keyword", "unknown"),
            "total_products": metadata.get("total_products", 0),
            "top_keywords": data.get("top_keywords", []),
            "difficulty_table": data.get("difficulty_table", []),
            "price_sweet_spot": data.get("price_sweet_spot", {}),
            "competitor_gaps": data.get("competitor_gaps", []),
            "title_patterns": data.get("title_patterns", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading report: {str(e)}")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
