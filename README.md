# 📊 ShopEasy — Marketing Analytics & AI Product Intelligence System

> **An end-to-end data pipeline integrating SQL, Python, Power BI, NLP, and cloud deployment into a single cohesive intelligence system.**

🌐 **Live Intelligence System:** [marketing-analytics-business-case.streamlit.app](https://marketing-analytics-business-case.streamlit.app/)

---

## 📌 What Is This?

This is not just a dashboard. It is an **AI-powered Product Intelligence System** built on top of a full marketing analytics pipeline. It transforms raw customer review data into structured health scores, root cause diagnoses, executive-level narratives, and growth playbooks — all accessible through a live, interactive web interface.

What started as a Business Intelligence project in SQL and Power BI evolved into a deployed system where any business stakeholder can open a browser, select a product, and immediately understand its health, its problems, and what to do next.

---

## 🗂️ Repository Structure

```
Marketing-Analytics-Business-Case/
│
├── app.py                                   # Streamlit intelligence system (main entry point)
├── ai_sentiment_decision_engine.py          # AI sentiment classification and decision logic
├── customer_reviews_enrichment.py           # NLP enrichment pipeline (VADER + issue detection)
│
├── outputs/                                 # Processed CSVs consumed by app.py
│   ├── review_intelligence_dataset_*.csv    # Enriched review-level data
│   └── product_summary_*.csv               # Aggregated product health metrics
│
├── SQLQuery1.sql – SQLQuery5.sql            # Data cleaning & transformation queries
├── fact_customer_reviews_with_sentiment.csv # Source review dataset with sentiment labels
│
├── Bi Report.pbix                           # Power BI report file
├── BI_report_Presentation.pptx             # BI layer slide deck
├── Marketing Analytics Business Case.pptx  # Full project presentation
├── PortfolioProject_MarketingAnalytics.bak  # SQL Server database backup
│
├── Visuals/                                 # Dashboard screenshots
├── requirements.txt                         # Python dependencies
└── README.md
```

---

## 🧭 Project Overview

**ShopEasy** is a fictional e-commerce business. The goal of this project is to answer three core business questions using data:

1. **Why is the conversion rate not higher?** — Identify funnel drop-off points and product-level gaps.
2. **What content is actually engaging customers?** — Measure social and marketing performance across channels.
3. **What are customers really saying?** — Turn unstructured review text into structured, actionable intelligence.

The project has two distinct layers: a **Power BI analytics dashboard** for business intelligence reporting, and a **Streamlit-based AI intelligence system** for real-time product health monitoring.

---

## 🏗️ Full System Architecture

```
📥  SQL Server  (Raw Marketing & Review Data)
        ↓
🗄️  SQL Cleaning & Preprocessing  (SQLQuery1–5.sql)
        ↓
🐍  Python ETL + NLP Sentiment Enrichment  (customer_reviews_enrichment.py)
        ↓
🤖  AI Sentiment Decision Engine  (ai_sentiment_decision_engine.py)
        ↓
📊  Product Intelligence Engine  (Health Score + Root Cause + Alerts)
        ↓
📊  Power BI Modeling  (DAX + Relationships + Visualizations)
        ↓
🌐  Streamlit AI Intelligence System  (Cloud Deployed via Streamlit Cloud)
```

---

## 🎛️ Intelligence System — Five Modules

The deployed Streamlit system is organized into five interactive modules accessible from the sidebar.

### 🏆 1. Product Rankings
A ranked leaderboard of all 20 products by **Overall Health Score**, with global filters for minimum review count and health status (Strong / Moderate / At Risk). A horizontal bar chart color-coded from red to green gives an instant portfolio-wide view.

### 🔍 2. Product Deep Dive
Select any product to see its full diagnostic profile:
- KPI cards: total reviews, positive/negative counts, health score
- Automated risk alert (Critical / Moderate / Stable) based on negative review threshold
- Donut chart for sentiment breakdown (Positive / Neutral / Negative)
- Health score gauge (-100 to +100)
- Horizontal complaint distribution bar chart
- Sentiment score histogram
- **Action Plan** — prioritized remediation steps for the top two detected issue categories
- **Growth Playbook** — product-specific growth strategies (e.g., sponsorship, bundle offers, viral campaigns)
- Raw top-5 positive and negative reviews

### ⚔️ 3. Side-by-Side Product Comparison
Compare any two products across all key dimensions:
- Metric delta cards (health score, positive %, negative %, average sentiment, review volume)
- Parallel sentiment donut charts
- Parallel health score gauges
- Parallel complaint breakdown charts
- **Multi-metric radar chart** (normalized across health, positivity, sentiment, and review volume)
- Automated **Verdict** declaring which product leads

### 📊 4. Data & Analysis
Portfolio-wide analytics beyond individual products:
- Scatter plot: Review Volume vs Health Score (bubble size = negative review count)
- **Issue heatmap** — all products × all issue types, showing complaint density
- Grouped bar chart: Positive vs Negative % by product
- Overall sentiment score distribution histogram
- **Raw Review Data Explorer** — filter by product, keyword search, and sentiment category

### 🤖 5. AI Executive Report
Two sub-modules powered by **Groq (Llama 3.3-70B)**:

**Executive Summary tab:** Select a product and click Generate. The AI reads the product's actual metrics, complaint breakdown, and sample reviews, then writes a 4–6 paragraph executive briefing covering health assessment, key strengths, critical risks with evidence, prioritized action items, and forward outlook. The summary streams live in the interface. A **Download PDF** button packages the metrics table and AI narrative into a formatted PDF report.

**Natural Language Search tab:** Ask plain-English questions about the product portfolio. The AI answers using the actual data — product summaries and issue counts — with specific product names and numbers. Previous questions are saved in a collapsible history within the session.

---

## 🧠 Intelligence Engine — How It Works

### Product Health Score
```
Health Score = Positive Review % − Negative Review %
Range: −100 to +100

> +20  →  Strong
−20 to +20  →  Moderate
< −20  →  At Risk
```

### NLP Sentiment Enrichment
- **VADER (Valence Aware Dictionary and sEntiment Reasoner)** from NLTK is applied to each review
- Outputs: `SentimentScore` (float), `SentimentCategory` (Positive / Neutral / Negative), `SentimentBucket`

### Root Cause Detection
Rule-based keyword classification assigns each negative review to one of eight issue categories:

| Issue Category | Example Triggers |
|---|---|
| Delivery Issue | late, shipping, arrived damaged |
| Product Quality | broke, defective, cheap material |
| Pricing Issue | overpriced, not worth, expensive |
| Customer Service | no response, rude, unhelpful |
| Packaging Issue | poor packaging, box damaged |
| Performance Issue | doesn't work, stopped working |
| Usability Issue | hard to use, confusing instructions |
| Expectation Gap | looks different, not as described |

### Automated Alert Thresholds
- **> 40% negative reviews** → 🚨 Critical Risk
- **25–40% negative reviews** → ⚠️ Moderate Risk
- **< 25% negative reviews** → ✅ Stable

---

## 📊 Power BI Dashboard — Four Pages

| Page | Description |
|---|---|
| **Overview** | KPI cards for Conversion Rate (9.6%), Total Views, Clicks, Likes, and Average Rating. High-level portfolio summary. |
| **Conversion Details** | Month-by-month and product-by-product conversion analysis with dynamic slicers. |
| **Social Media Details** | Engagement metrics (views, clicks, likes) across marketing content types, with trend lines. |
| **Customer Reviews** | NLP sentiment classification visualized per product, with positive/negative/neutral breakdown. |

---

## 💡 Key Business Insights

- 🏒 **Hockey Stick** achieved the highest product conversion rate at **15.5%**, followed by Ski Boots and Baseball Glove.
- 📉 **February** showed a noticeable dip in conversions, pointing to seasonal or campaign gaps.
- 💬 Over **61% of all customer reviews** carried positive sentiment.
- ❤️ High sentiment scores were strongly correlated with higher product ratings.
- 📦 **Delivery** and **Product Quality** were the most frequently detected negative review themes across the portfolio.
- 🚨 The Health Score model enabled rapid identification of at-risk products before they became critical.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Storage | SQL Server |
| Data Cleaning | SQL (T-SQL) |
| ETL & NLP | Python — Pandas, NLTK (VADER) |
| Visualization Layer | Python — Plotly, Plotly Express |
| BI Reporting | Power BI Desktop (DAX, Power Query) |
| AI Narrative Generation | Groq API — Llama 3.3-70B Versatile |
| PDF Generation | ReportLab |
| Intelligence System UI | Streamlit |
| Deployment | Streamlit Cloud |
| Version Control | GitHub |

---

## ⚙️ Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/mayankbungla/Marketing-Analytics-Business-Case.git
cd Marketing-Analytics-Business-Case
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your Groq API key
The AI Executive Report module requires a Groq API key. Set it as an environment variable:
```bash
export GROQ_API_KEY=your_key_here
```
Or add it to `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_key_here"
```

### 4. Generate the processed data files
Run the enrichment pipeline to produce the `outputs/` CSVs that the intelligence system reads:
```bash
python customer_reviews_enrichment.py
```

### 5. Launch the intelligence system
```bash
streamlit run app.py
```

---

## 📁 Data Pipeline Details

The system relies on two pre-processed CSV files in the `outputs/` folder:

- `review_intelligence_dataset_*.csv` — one row per customer review, enriched with sentiment score, sentiment category, and detected issue
- `product_summary_*.csv` — one row per product, aggregated with total reviews, positive/negative counts, percentages, average sentiment, and health score

These are generated by `customer_reviews_enrichment.py` from the source file `fact_customer_reviews_with_sentiment.csv`.

---

## 🔗 Connect

**📧 Email:** mayankbungla8@gmail.com  
**🔗 LinkedIn:** [linkedin.com/in/mayankbungla](https://www.linkedin.com/in/mayankbungla/)  
**🐙 GitHub:** [github.com/mayankbungla](https://github.com/mayankbungla)

---

*Built by Mayank Bungla — from raw SQL data to a deployed AI intelligence system.*
