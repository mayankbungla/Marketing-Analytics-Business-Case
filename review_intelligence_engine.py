# =========================================================
# REVIEW INTELLIGENCE ENGINE 
# =========================================================

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = "fact_customer_reviews_with_sentiment.csv"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# =========================================================
# ROOT CAUSE KEYWORDS
# =========================================================

ISSUE_KEYWORDS = {

    "Delivery Issue": [
        "late", "delay", "delayed", "delivery", "shipping",
        "arrived late", "not delivered", "delivery delay",
        "shipping issue", "courier", "lost package",
        "slow delivery", "took too long"
    ],

    "Product Quality": [
        "broken", "defective", "poor quality", "damaged",
        "not working", "cheap", "faulty", "low quality",
        "build quality", "poor build", "material feels cheap"
    ],

    "Pricing Issue": [
        "expensive", "overpriced", "costly", "price high",
        "not worth", "worth the money", "value for money",
        "could be cheaper", "too expensive",
        "waste of money"
    ],

    "Customer Service": [
        "support", "customer service", "no response",
        "rude", "helpdesk", "terrible service",
        "bad service", "refund issue", "no refund",
        "unhelpful"
    ],

    "Packaging Issue": [
        "packaging", "box damaged", "poor packaging",
        "torn box", "open box", "damaged packaging"
    ],

    "Performance Issue": [
        "stopped working", "broke", "performance issue",
        "slow", "lag", "overheating", "heating issue",
        "battery issue", "battery drained", "not durable"
    ],

    "Usability Issue": [
        "instructions unclear", "unclear instructions",
        "hard to use", "confusing", "difficult to use",
        "setup problem"
    ],

    "Expectation Gap": [
        "average experience", "nothing special",
        "did not meet expectations",
        "not as expected", "disappointed",
        "bad experience"
    ]
}

# =========================================================
# ISSUE DETECTION
# =========================================================

def detect_issues(text):
    text_lower = str(text).lower()
    found = []

    for issue, keywords in ISSUE_KEYWORDS.items():
        if any(word in text_lower for word in keywords):
            found.append(issue)

    return ", ".join(found) if found else "No Issue Detected"


# =========================================================
# PRODUCT HEALTH METRICS
# =========================================================

def create_product_summary(df):

    # 🔥 FIXED: Include ProductName in groupby
    summary = (
        df.groupby(["ProductID", "ProductName"])
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

    summary["HealthScore"] = (
        summary["PositivePct"] - summary["NegativePct"]
    )

    return summary.sort_values("HealthScore", ascending=False)


# =========================================================
# MAIN
# =========================================================

def main():

    print("Running Review Intelligence Engine...")

    df = pd.read_csv(INPUT_FILE)

    print("Loaded:", df.shape)

    # Safety check
    if "ProductName" not in df.columns:
        raise ValueError("ProductName column not found in dataset. "
                         "Ensure enrichment script includes ProductName.")

    df["DetectedIssue"] = df["ReviewText"].apply(detect_issues)

    product_summary = create_product_summary(df)

    timestamp = datetime.now().strftime("%Y%m%d")

    df.to_csv(
        OUTPUT_DIR / f"review_intelligence_dataset_{timestamp}.csv",
        index=False
    )

    product_summary.to_csv(
        OUTPUT_DIR / f"product_summary_{timestamp}.csv",
        index=False
    )

    print("Intelligence files generated successfully.")


if __name__ == "__main__":
    main()