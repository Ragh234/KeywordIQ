# Comprehensive Technical Report: Amazon Keyword Research SaaS Platform

## 1. Executive Summary
This project is a highly scalable, multi-service Software as a Service (SaaS) platform built for e-commerce sellers. It automates the process of scraping Amazon product pages and applies sophisticated Natural Language Processing (NLP) and Artificial Intelligence models to extract high-value seller keywords, analyze competitor gaps, calculate price "sweet spots", and estimate keyword ranking difficulty.

The system relies on a **MERN (MongoDB, Express, React, Node.js)** stack for its user interface and secure access portal, integrated seamlessly with an **asynchronous Python/FastAPI microservice** that acts as the core Data Science and Web Scraping engine.

---

## 2. Full Technology Stack
### Frontend (User Interface & Client)
- **Framework:** React.js integrated with Vite for extremely fast Hot Module Replacement (HMR) and optimized builds.
- **Styling:** Tailwind CSS, utilizing a modern "Glassmorphism" UI paradigm.
- **State Management & Routing:** React Router v7.
- **API Communication:** Axios.
- **Icons:** Lucide React.

### Backend (Client Gateway API & Authentication)
- **Runtime:** Node.js.
- **Framework:** Express.js.
- **Database:** MongoDB, abstracted via Mongoose ODM.
- **Authentication:** JSON Web Tokens (JWT) for stateless sessions with `bcryptjs` for secure password hashing.

### Data Science Microservice & Web Scraping
- **API Framework:** FastAPI (Python), utilizing `asyncio`.
- **Concurrency Setup:** `ThreadPoolExecutor` handles blocking IO so the API can scale concurrent scraping requests without server blockage.
- **Web Scraping:** Playwright (headless Chromium) configured with anti-bot/stealth features.
- **Data Manipulation:** Pandas & NumPy for vectorized dataframe operations.
- **Machine Learning / NLP:** `scikit-learn` (specifically `TfidfVectorizer`).

---

## 3. Web Scraping & Data Ingestion Architecture
The web scraper is built using **Playwright** injected with automated anti-detection bypasses:
- Disables HTTP features that flag bots (`--disable-blink-features=AutomationControlled`).
- Strips the `navigator.webdriver` property via JavaScript injection before page-load.
- Uses random human-mimicking delay distribution (`random.uniform`) before pagination to dodge Amazon CAPTCHA detection.
- Retries upon failure or network timeout (Network healing).

### Data Normalization & Cleaning Pipeline
Data is ingested as raw DOM strings and scrubbed via Python `Regular Expressions (regex)`. 
- **Prices:** Formatted recursively, stripping commas and currency markers (e.g., "₹1,54,990" → `154990.0`).
- **Ratings:** Extracting baseline floats (e.g., "4.3 out of 5" → `4.3`).
- Missing nodes are dynamically filled via localized `NaN` assignment without crashing the dataframe pipeline.

---

## 4. Reverse-Engineered A9 Ranking Engine
A critical module in this system is the `composite_a9_score()`. Amazon's A9 search algorithm is proprietary, so this project implements a reversed mathematical approximation utilizing five configurable weights. The score places each product on a localized `[0, 1]` index scale.

1. **Text Relevance (30% weight):** Assesses the phrase match ratio of the search term against the product title. It evaluates subset token arrays and scales the score based on match percentage.
2. **Sales Velocity Proxy (25% weight):** Uses review counts as a trailing indicator of sales. Because reviews grow exponentially, the algorithm uses a **Log-Scale Normalization** (`math.log1p()`) to prevent products with 50,000 reviews from entirely eclipsing products with 1,000 reviews.
3. **Customer Satisfaction (15% weight):** Implements a **Sigmoid Mapping Curve** (`1.0 / (1.0 + e^(-3.0 * (rating - 3.8)))`). This mathematically punishes products under 3.5 stars severely while flattening out the benefit difference between a 4.6 and a 4.8.
4. **Price Competitiveness (15% weight):** Utilizes a **Gaussian Distance** formula (a bell curve). It maps the distance (`z-score`) of a product's price from the computed category median. Both extremely cheap and outrageously expensive items are penalized.
5. **Observed Rank Position (15% weight):** Provides an **Inverse-Log Decay** point distribution giving significantly more value to the transition from Rank 1→5 than Rank 15→20.

---

## 5. NLP Keyword Extraction & Matrix Analysis
The platform processes scraped product titles using `scikit-learn` to figure out which feature keywords are actually driving traffic and relevance.

### Tokenization & Noise Filtering
Product titles run through a regex-lowercasing tokenizer. The engine eliminates standard English stopwords ("and", "the", "for") but ALSO custom-filters Amazon e-commerce filler terms ("bundle", "prime", "compatible with", "pack", "free").

### TF-IDF Vectorization
The engine calculates **Term Frequency - Inverse Document Frequency (TF-IDF)** to isolate statistical relevance over pure occurrence. Using ranges `(1, 3)`, it extracts Uni-Grams (1 word), Bi-Grams (2 words), and Tri-Grams (3 words).

### The Composite Keyword Value Equation
Because counting keywords isn't enough, each extracted keyword is rigorously scored via:
- **Frequency (35%):** Pure occurrence distribution.
- **TF-IDF Variance (25%):** The word's statistical significance across the product cluster.
- **Rank-Weighted Frequency (25%):** A keyword is deemed highly important if it shows up in products sitting at Rank #1 through #5, compared to Rank #20 through #30.
- **Position Average Penalty (15%):** Penalizes keywords whose host-products average poor search trajectories.
- **Anomaly Detection Filter:** Keywords must represent at least a 10% saturation rate minimum, completely filtering out unique competitor brand names that happen to appear near the top.

---

## 6. Competitor Gaps & Difficulty Metrics
The backend finishes its analysis by running several market computations:
- **Competitor Gaps Calculation:** Automatically cross-pollinates the dataframe into 'Top N' and 'Bottom N' groups. By running percentile evaluations, the code identifies "Gap Keywords" that Top Ranked products heavily utilize but Bottom Ranked products completely lack.
- **Keyword Ranking Difficulty:** Uses a **Weighted Harmonic Mean** (60/40 Review-Rating Split) formula, scoring a keyword's difficulty [0 - 100] based on the combined rating dominance and review-wall of the incumbents on page 1.
- **Price Sweet Spot Analytics:** Calculates the Interquartile Range (25th and 75th percentiles) strictly inside the "Top Ranked" items dataframe, telling the seller exactly what price boundary converts the best in the organic search results algorithm.
