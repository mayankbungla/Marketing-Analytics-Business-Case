# =========================================================
# Review Intelligence Engine (ADDITIONAL FEATURE)
# Purpose: Help business identify problem products & causes
# =========================================================

# pip install pandas numpy nltk

import pandas as pd
import numpy as np
import nltk
from datetime import datetime
from pathlib import Path

nltk.download("vader_lexicon", quiet=True)

# =========================================================
# 1. CONFIG
# =========================================================

INPUT_FILE = "fact_customer_reviews_with_sentiment.csv"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================================================
# 2. ROOT CAUSE KEYWORDS (THE "WHY")
# =========================================================

ISSUE_KEYWORDS = {
    "Delivery Issue": [
        "late", "delay", "delayed", "delivery", "shipping",
        "arrived late", "not delivered"
    ],
    "Product Quality": [
        "broken", "defective", "poor quality", "damaged",
        "not working", "cheap"
    ],
    "Pricing Issue": [
        "expensive", "overpriced", "costly", "price high"
    ],
    "Customer Service": [
        "support", "customer service", "no response",
        "rude", "helpdesk"
    ],
    "Packaging Issue": [
        "packaging", "box damaged", "poor packaging"
    ]
}

# =========================================================
# 3. ISSUE DETECTION
# =========================================================

def detect_issues(text: str) -> str:
    """Detect complaint themes inside review text."""
    text_lower = str(text).lower()
    found = []

    for issue, keywords in ISSUE_KEYWORDS.items():
        if any(word in text_lower for word in keywords):
            found.append(issue)

    if not found:
        return "No Issue Detected"

    return ", ".join(found)

# =========================================================
# 4. PRODUCT HEALTH METRICS
# =========================================================

def create_product_health(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product-level sentiment KPIs."""

    summary = (
        df.groupby("ProductID")
        .agg(
            TotalReviews=("ReviewID", "count"),
            AvgSentiment=("SentimentScore", "mean"),
            NegativeReviews=("SentimentScore", lambda x: (x < -0.05).sum()),
            PositiveReviews=("SentimentScore", lambda x: (x > 0.05).sum())
        )
        .reset_index()
    )

    summary["NegativePct"] = (
        summary["NegativeReviews"] / summary["TotalReviews"] * 100
    )

    summary["PositivePct"] = (
        summary["PositiveReviews"] / summary["TotalReviews"] * 100
    )

    # Risk tagging (business friendly)
    summary["ProductHealth"] = np.where(
        summary["NegativePct"] > 40,
        "High Risk",
        np.where(summary["PositivePct"] > 60, "Excellent", "Monitor")
    )

    return summary

# =========================================================
# 5. BUSINESS INSIGHT GENERATOR
# =========================================================

def generate_business_insights(product_summary: pd.DataFrame,
                               review_df: pd.DataFrame) -> list:
    """Create executive-friendly insights."""

    insights = []

    worst_product = product_summary.sort_values(
        "NegativePct", ascending=False
    ).iloc[0]

    best_product = product_summary.sort_values(
        "PositivePct", ascending=False
    ).iloc[0]

    top_issue = review_df["DetectedIssue"].value_counts().idxmax()

    insights.append(
        f"Product {worst_product['ProductID']} shows the highest negative sentiment ({worst_product['NegativePct']:.1f}%). Immediate investigation recommended."
    )

    insights.append(
        f"Product {best_product['ProductID']} has the strongest customer satisfaction ({best_product['PositivePct']:.1f}%). Consider promoting this product."
    )

    insights.append(
        f"Most common customer complaint category: {top_issue}."
    )

    insights.append(
        "Recommended Action: Focus on fixing delivery and quality issues to improve conversion rates."
    )

    return insights

# =========================================================
# 6. MAIN PIPELINE
# =========================================================

def main():

    print("🚀 Running Review Intelligence Engine...")

    # -----------------------
    # Load enriched data
    # -----------------------
    df = pd.read_csv(INPUT_FILE)

    print("✅ Data loaded:", df.shape)

    # -----------------------
    # Detect issues (WHY)
    # -----------------------
    print("🔎 Detecting complaint themes...")
    df["DetectedIssue"] = df["ReviewText"].apply(detect_issues)

    # -----------------------
    # Product health
    # -----------------------
    print("📊 Computing product health metrics...")
    product_summary = create_product_health(df)

    # -----------------------
    # Generate insights
    # -----------------------
    print("🧠 Generating business insights...")
    insights = generate_business_insights(product_summary, df)

    # -----------------------
    # Save outputs
    # -----------------------
    timestamp = datetime.now().strftime("%Y%m%d")

    df.to_csv(
        OUTPUT_DIR / f"review_intelligence_output_{timestamp}.csv",
        index=False
    )

    product_summary.to_csv(
        OUTPUT_DIR / f"product_health_summary_{timestamp}.csv",
        index=False
    )

    # UTF-8 safe write
    with open(
        OUTPUT_DIR / f"business_insights_{timestamp}.txt",
        "w",
        encoding="utf-8"
    ) as f:
        for line in insights:
            f.write(line + "\n")

    print("\n🎯 KEY INSIGHTS:")
    for line in insights:
        print("•", line)

    print("\n✅ Review Intelligence Engine completed.")

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()