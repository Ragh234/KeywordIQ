# KeywordIQ

[![CI](https://github.com/Ragh234/KeywordIQ/actions/workflows/ci.yml/badge.svg)](https://github.com/Ragh234/KeywordIQ/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An Amazon keyword-research SaaS platform: scrape a search results page,
clean and score the listed products, and surface which keywords are worth
targeting — with a composite A9-style importance score, not just raw
frequency.

Full write-up of the scoring algorithm: [docs/Project_Architecture_and_Algorithms_Report.md](docs/Project_Architecture_and_Algorithms_Report.md)

## Features

- **Keyword research:** TF-IDF n-gram extraction ranked by a composite importance score, with per-keyword difficulty.
- **Top products by A9 score:** the 20 best-scoring products, each with a bar showing how its five score factors (relevance, sales, rating, price, rank) contribute. This is an estimate, not Amazon's real algorithm.
- **Suggested listing title:** a rule-based title (about 120 characters, phrases before single words) built from the top and competitor-gap keywords, editable in the UI with a live 200-character counter and a Copy button. It is a draft: remove any competitor brand names that slip in.
- **Competitor gaps, price sweet spot, and title patterns** (top 10 vs the rest).
- **Accounts and history:** sign up, save reports, reopen or delete them later.

## Architecture

Four independent pieces, each replaceable on its own:

```text
┌──────────────┐   HTTP    ┌────────────────┐   HTTP    ┌───────────────────┐
│   frontend/  │──/api────▶│    server/     │──────────▶│      api/          │
│  React+Vite  │◀──────────│ Express+Mongo  │◀──────────│   FastAPI          │
└──────────────┘  proxy    │ auth + reports │  proxies  │ wraps the package  │
                            └────────────────┘  /analyze │       below        │
                                                          └─────────┬─────────┘
                                                                    │ imports
                                                          ┌─────────▼─────────┐
                                                          │ amazon_keyword_   │
                                                          │ tool/ (Python pkg)│
                                                          │ scrape → clean →  │
                                                          │ extract → score   │
                                                          └───────────────────┘
```

| Layer | Path | Role |
|---|---|---|
| Core package | [`amazon_keyword_tool/`](amazon_keyword_tool/) | Playwright scraper → BeautifulSoup parser → pandas cleaning → TF-IDF keyword extraction → composite scoring. Importable and independently testable; also runnable as a CLI. |
| Analysis API | [`api/main.py`](api/main.py) | FastAPI wrapper that runs the package's scraper+analysis in a `ThreadPoolExecutor` (Playwright is sync) and exposes `/api/analyze` and `/api/health`. |
| App backend | [`server/`](server/) | Express + MongoDB. Owns user auth (JWT, bcrypt) and saved-report storage; proxies analysis requests to the FastAPI service (`PYTHON_API_URL`). |
| Frontend | [`frontend/`](frontend/) | React (Vite) dashboard — search, report view, history, auth pages. Vite dev server proxies `/api` to the Express server. |

## Why a composite score instead of raw keyword frequency

A keyword that appears in 40% of listings but only on page 3 of results is
worth less than one appearing in 15% of listings that are ranked #1–5.
[`amazon_keyword_tool/analysis/scoring.py`](amazon_keyword_tool/analysis/scoring.py)
blends five weighted signals — frequency, TF-IDF significance, rank-weighted
frequency, price competitiveness, and average search position — into a
single importance score per keyword. Weights live in
[`amazon_keyword_tool/config.py`](amazon_keyword_tool/config.py)
(`SCORE_WEIGHTS`).

## Run it locally

You need four terminals (or run each piece as you need it — the frontend
and server aren't required to use the Python package on its own).

**1. Python package** (scraper + analysis) — used directly by both the CLI and the FastAPI service:

```bash
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
playwright install chromium
```

**2. FastAPI analysis service** (port 8000):

```bash
uvicorn api.main:app --reload --port 8000
```

**3. Express API** (port 5000) — needs Mongo running and a root `.env` (see below):

```bash
cd server
npm install
npm run dev
```

**4. React frontend** (port 5173, proxies `/api` → `:5000`):

```bash
cd frontend
npm install
npm run dev
```

### Environment variables

Copy `.env.example` to `.env` in the project root — `server/index.js` loads
it from there, not from `server/.env`:

```bash
cp .env.example .env
```

| Variable | Used by | Notes |
|---|---|---|
| `MONGO_URI` | `server/` | MongoDB connection string. |
| `JWT_SECRET` | `server/` | Signs/verifies auth tokens. |
| `PORT` | `server/` | Express port, defaults to `5000`. |
| `PYTHON_API_URL` | `server/` | Where the Express API proxies `/analyze` to. Defaults to `http://127.0.0.1:8000`. |

### CLI usage (Python package alone, no server/frontend needed)

```bash
python -m amazon_keyword_tool.cli --keyword "wireless earbuds" --top-n 20
```

## Tests

```bash
pip install -r requirements.txt
pytest tests/
```

`tests/` covers cleaning, extraction, scoring, the title builder, the FastAPI
endpoints (scraping stubbed out), and the CLI's integration path against fixture data — no live network calls or browser required. The
three `scripts/test_*.py` files are separate manual probes against a real
Amazon page (need `playwright install chromium` and network access); they
are not part of the automated suite.

## Known trade-offs

- `api/main.py` has no authentication and no CORS middleware. It is meant to be
  called only by the Express server (server to server), so keep it on a private
  network and never expose it to browsers or the public internet.
- Scraping amazon.in directly is fragile to markup/selector changes by
  design of the exercise; `SEARCH_SELECTORS` in `config.py` is the single
  place to update if Amazon changes its DOM.

## Author

Raghav Malani
