# reporting/export.py — CSV and JSON export of keyword research results

"""
Exports KeywordReport data to disk in CSV and/or JSON format.

Outputs written to the OUTPUT_DIR defined in config.py.
"""

import csv
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from amazon_keyword_tool.analysis.keyword_research import KeywordReport
from amazon_keyword_tool.config import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _safe_keyword_slug(keyword: str) -> str:
    """Convert a search keyword into a filesystem-safe slug."""
    import re
    slug = re.sub(r"[^a-z0-9]+", "_", keyword.lower().strip())
    return slug[:40] if slug else "unknown"


def _ensure_output_dir() -> Path:
    path = Path(OUTPUT_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


# ── Per-report export functions ───────────────────────────────────────────────

def export_keywords_csv(report: KeywordReport, directory: Optional[str] = None) -> str:
    """
    Export the top_keywords list to a CSV file.

    Columns: rank, keyword, importance, frequency, avg_rank, tfidf_score,
             rank_weighted_freq, difficulty
    """
    out_dir  = Path(directory) if directory else _ensure_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug     = _safe_keyword_slug(report.search_keyword)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = out_dir / f"keywords_{slug}_{ts}.csv"

    rows = []
    for i, kw in enumerate(report.top_keywords, 1):
        diff = None
        if not report.difficulty_table.empty and "keyword" in report.difficulty_table.columns:
            match = report.difficulty_table[report.difficulty_table["keyword"] == kw.keyword]
            if not match.empty:
                diff = match.iloc[0]["difficulty"]
        rows.append({
            "rank":               i,
            "keyword":            kw.keyword,
            "importance":         round(kw.importance, 4),
            "frequency":          kw.frequency,
            "avg_rank":           round(kw.avg_rank, 2),
            "tfidf_score":        round(kw.tfidf_score, 4),
            "rank_weighted_freq": round(kw.rank_weighted_freq, 4),
            "difficulty":         round(diff, 1) if diff is not None else None,
        })

    if rows:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        logger.info(f"Keywords CSV → {filepath}")
    else:
        logger.warning("No keywords to export.")

    return str(filepath)


def export_products_csv(report: KeywordReport, directory: Optional[str] = None) -> str:
    """
    Export the scored products DataFrame to a CSV file.
    """
    out_dir  = Path(directory) if directory else _ensure_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug     = _safe_keyword_slug(report.search_keyword)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = out_dir / f"products_scored_{slug}_{ts}.csv"

    if not report.scored_products_df.empty:
        report.scored_products_df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info(f"Scored products CSV → {filepath}")
    else:
        logger.warning("No scored products to export.")

    return str(filepath)


def export_report_json(report: KeywordReport, directory: Optional[str] = None) -> str:
    """
    Export the full KeywordReport as a structured JSON file.

    Includes:
      - metadata (keyword, timestamp, product count)
      - top_keywords list
      - price_sweet_spot dict
      - competitor_gaps list
      - difficulty table
      - title_patterns table
    """
    out_dir  = Path(directory) if directory else _ensure_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug     = _safe_keyword_slug(report.search_keyword)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = out_dir / f"report_{slug}_{ts}.json"

    def _df_to_records(df: pd.DataFrame) -> list[dict]:
        if df is None or df.empty:
            return []
        return df.where(df.notna(), None).to_dict("records")

    payload = {
        "metadata": {
            "search_keyword":  report.search_keyword,
            "total_products":  report.total_products,
            "generated_at":    datetime.now().isoformat(),
        },
        "top_keywords": [
            {
                "keyword":            kw.keyword,
                "importance":         round(kw.importance, 4),
                "frequency":          kw.frequency,
                "avg_rank":           round(kw.avg_rank, 2),
                "tfidf_score":        round(kw.tfidf_score, 4),
                "rank_weighted_freq": round(kw.rank_weighted_freq, 4),
            }
            for kw in report.top_keywords
        ],
        "price_sweet_spot":  report.price_sweet_spot,
        "competitor_gaps":   report.competitor_gaps,
        "difficulty_table":  _df_to_records(report.difficulty_table),
        "title_patterns":    _df_to_records(report.title_patterns),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)

    logger.info(f"Report JSON → {filepath}")
    return str(filepath)


# ── Convenience: export all ───────────────────────────────────────────────────

def export_all(report: KeywordReport, directory: Optional[str] = None) -> dict[str, str]:
    """
    Export keywords CSV, scored products CSV, and full JSON report.

    Returns:
        dict mapping {'keywords_csv', 'products_csv', 'report_json'} → file paths
    """
    return {
        "keywords_csv":  export_keywords_csv(report, directory),
        "products_csv":  export_products_csv(report, directory),
        "report_json":   export_report_json(report, directory),
    }
