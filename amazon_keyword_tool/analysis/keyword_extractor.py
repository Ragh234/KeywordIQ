# keyword_extractor.py — TF-IDF + n-gram keyword extraction from product titles

"""
Extracts meaningful keywords and phrases from Amazon product titles.

Pipeline:
    1. Tokenise + remove stopwords (English + Amazon-specific filler)
    2. Build n-grams (unigrams, bigrams, trigrams)
    3. Score with TF-IDF across all titles in the result set
    4. Aggregate frequency and rank-weighted importance per keyword

Output: a list of KeywordInfo objects sorted by composite importance.
"""

import re
import logging
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

# ── Stopwords ──────────────────────────────────────────────────────────────────
# Standard English stopwords + Amazon-specific noise
STOPWORDS: set[str] = {
    # English
    "a","an","the","and","or","for","in","on","at","to","of","with",
    "is","it","its","this","that","these","those","are","was","were",
    "be","been","being","have","has","had","do","does","did","will",
    "would","could","should","may","might","shall","can","by","from",
    "as","into","through","during","before","after","above","below",
    "up","down","out","off","over","under","again","further","then",
    "once","here","there","when","where","why","how","all","both",
    "each","few","more","most","other","some","such","no","not","only",
    "own","same","so","than","too","very","s","t","just","but","if",
    "new", "best", "top",
    # Amazon listing noise
    "combo", "pack", "set", "bundle", "kit", "unit", "piece", "pieces",
    "buy", "get", "free", "sale", "deal", "offer", "discount",
    "compatible", "compatible with", "suitable", "suitable for",
    "amazon", "fulfilled", "prime", "certified",
    "model", "black", "white", "grey", "gray", "silver", "gold", "blue",
    "red", "green", "navy",
}


def _tokenise(text: str) -> list[str]:
    """Lowercase, strip punctuation, return individual word tokens."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    tokens = [t for t in text.split() if len(t) > 1 and t not in STOPWORDS]
    return tokens


def _build_ngrams(tokens, max_n=3):
    """Return all n-grams (1 to max_n) as space-joined strings."""
    ngrams = []
    for n in range(1, max_n + 1):
        for i in range(len(tokens) - n + 1):
            ngrams.append(" ".join([tokens[j] for j in range(i, i + n)]))
    return ngrams


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class KeywordInfo:
    """Represents a single keyword/phrase extracted from product titles."""
    keyword:      str
    frequency:    int            # # of products whose title contains this keyword
    tfidf_score:  float          # average TF-IDF score across titles
    avg_rank:     float          # avg rank position of products containing this keyword
    rank_weighted_freq: float    # frequency weighted by inverse rank (top ranks count more)
    importance:   float = 0.0   # composite importance score (set after normalisation)

    def __repr__(self) -> str:
        return (
            f"KeywordInfo({self.keyword!r}, freq={self.frequency}, "
            f"tfidf={self.tfidf_score:.3f}, avg_rank={self.avg_rank:.1f}, "
            f"importance={self.importance:.3f})"
        )


# ── Core extraction functions ──────────────────────────────────────────────────

def compute_tfidf(titles: list[str], ngram_range: tuple[int, int] = (1, 3)) -> dict[str, float]:
    """
    Compute TF-IDF scores for all n-gram terms across a list of titles.

    Returns:
        dict mapping each term → its mean TF-IDF score across all documents
    """
    if not titles:
        return {}

    # Preprocess titles for TF-IDF
    processed = []
    for t in titles:
        tokens = _tokenise(t)
        processed.append(" ".join(tokens))

    # Guard against all-empty after cleaning
    if not any(processed):
        return {}

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            min_df=1,
            max_df=0.95,
            analyzer="word",
        )
        matrix = vectorizer.fit_transform(processed)
        feature_names = vectorizer.get_feature_names_out()

        # Mean TF-IDF per term across all documents
        mean_scores = matrix.mean(axis=0).A1  # ndarray
        return {term: float(score) for term, score in zip(feature_names, mean_scores)}

    except ValueError as e:
        logger.warning(f"TF-IDF failed: {e}")
        return {}


def extract_keywords(
    df: pd.DataFrame,
    ngram_range: tuple[int, int] = (1, 3),
    top_n: int = 50,
) -> list[KeywordInfo]:
    """
    Extract and rank keywords from a cleaned products DataFrame.

    Args:
        df:          Cleaned DataFrame (must have 'title' and 'rank_position' columns)
        ngram_range: Min/max n-gram sizes
        top_n:       How many top keywords to return

    Returns:
        List of KeywordInfo objects sorted by composite importance (descending)
    """
    titles = df["title"].dropna().astype(str).tolist()
    if not titles:
        logger.warning("No titles found in DataFrame.")
        return []

    # 1. Compute TF-IDF scores
    tfidf_scores = compute_tfidf(titles, ngram_range=ngram_range)

    # 2. Per-title n-gram extraction, tracking rank positions
    total_products = len(df)
    rank_col = df["rank_position"].fillna(total_products + 1).astype(float).tolist()

    keyword_ranks: dict[str, list[float]] = defaultdict(list)   # keyword → [rank, ...]
    keyword_freqs: Counter = Counter()

    for idx, row in df.iterrows():
        title = str(row.get("title", "")) if pd.notna(row.get("title")) else ""
        rank  = float(row.get("rank_position", total_products + 1))
        if not title:
            continue
        tokens = _tokenise(title)
        ngrams = _build_ngrams(tokens, max_n=ngram_range[1])
        for gram in set(ngrams):    # use set so each keyword counted once per product
            keyword_ranks[gram].append(rank)
            keyword_freqs[gram] += 1

    if not keyword_freqs:
        logger.warning("No keywords extracted from titles.")
        return []

    # 3. Build KeywordInfo objects
    results = []
    
    # AGGRESSIVE FILTER: Require keywords to appear in at least 10% of products (minimum 4).
    # This completely eliminates competitor brands that appear in only a few sponsored/organic spots,
    # leaving only generic features (like "digital", "analog", "men", etc.).
    min_freq = max(4, int(total_products * 0.10))
    
    for kw, freq in keyword_freqs.items():
        if freq < min_freq:
            continue
            
        ranks = keyword_ranks[kw]
        avg_rank = sum(ranks) / len(ranks)
        # Rank-weighted: products at rank 1 contribute more than rank 20
        rank_weight = sum(1.0 / r for r in ranks if r > 0)

        info = KeywordInfo(
            keyword=kw,
            frequency=freq,
            tfidf_score=tfidf_scores.get(kw, 0.0),
            avg_rank=avg_rank,
            rank_weighted_freq=rank_weight,
        )
        results.append(info)

    # 4. Normalise metrics and compute composite importance
    if not results:
        return []

    max_freq        = max(r.frequency for r in results) or 1
    max_tfidf       = max(r.tfidf_score for r in results) or 1
    max_rwf         = max(r.rank_weighted_freq for r in results) or 1
    max_rank        = max(r.avg_rank for r in results) or 1

    for r in results:
        freq_norm  = r.frequency / max_freq
        tfidf_norm = r.tfidf_score / max_tfidf
        rwf_norm   = r.rank_weighted_freq / max_rwf
        # Lower avg rank = better; invert and normalise
        rank_norm  = 1.0 - (r.avg_rank / (max_rank + 1))

        # Composite importance weights
        r.importance = (
            0.35 * freq_norm   +   # how often it appears
            0.25 * tfidf_norm  +   # statistical significance
            0.25 * rwf_norm    +   # rank-weighted frequency (top of page matters)
            0.15 * rank_norm       # found in higher-ranking products
        )

    # 5. Sort and return top N
    results.sort(key=lambda x: x.importance, reverse=True)
    return [r for i, r in enumerate(results) if i < top_n]


def keyword_frequency_by_rank(
    df: pd.DataFrame,
    top_n: int = 10,
    rank_threshold: int = 10,
) -> pd.DataFrame:
    """
    Return a DataFrame comparing keyword frequency in top-ranked vs
    bottom-ranked products. Useful for spotting title patterns that correlate
    with better ranking.

    Args:
        df:              Cleaned products DataFrame
        top_n:           Number of top keywords to compare
        rank_threshold:  Products ranked ≤ this value are "top" products

    Returns:
        DataFrame with columns: keyword, top_freq, bottom_freq, top_pct, bottom_pct
    """
    if df.empty or "rank_position" not in df.columns:
        return pd.DataFrame()

    top_df    = df[df["rank_position"] <= rank_threshold]
    bottom_df = df[df["rank_position"] > rank_threshold]

    def count_kw(sub_df: pd.DataFrame) -> Counter:
        counts: Counter = Counter()
        for title in sub_df["title"].dropna():
            tokens = _tokenise(str(title))
            ngrams = _build_ngrams(tokens, max_n=2)
            for gram in set(ngrams):
                counts[gram] += 1
        return counts

    top_counts    = count_kw(top_df)
    bottom_counts = count_kw(bottom_df)

    top_total    = len(top_df) or 1
    bottom_total = len(bottom_df) or 1

    all_kw = set(top_counts) | set(bottom_counts)
    rows = []
    for kw in all_kw:
        tf = top_counts.get(kw, 0)
        bf = bottom_counts.get(kw, 0)
        rows.append({
            "keyword":     kw,
            "top_freq":    tf,
            "bottom_freq": bf,
            "top_pct":     round(float(tf / top_total * 100), 1),
            "bottom_pct":  round(float(bf / bottom_total * 100), 1),
        })

    result = pd.DataFrame(rows)
    if result.empty:
        return result

    # Sort by difference in top vs bottom presence — most discriminative first
    result["gap"] = result["top_pct"] - result["bottom_pct"]
    result = result.sort_values("gap", ascending=False).head(top_n).reset_index(drop=True)
    return result
