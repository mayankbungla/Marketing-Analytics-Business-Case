# pip install nltk pandas sqlalchemy pyodbc

import pandas as pd
from sqlalchemy import create_engine
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# -------------------------------
# Download VADER lexicon
# -------------------------------
nltk.download("vader_lexicon", quiet=True)


def calculate_sentiment(text, analyzer):
    text = str(text)
    score = analyzer.polarity_scores(text)
    return score["compound"]


def categorize_sentiment(score, rating):
    rating = 0 if pd.isna(rating) else rating

    if score > 0.05:
        if rating >= 4:
            return "Positive"
        elif rating == 3:
            return "Mixed Positive"
        else:
            return "Mixed Negative"

    elif score < -0.05:
        if rating <= 2:
            return "Negative"
        elif rating == 3:
            return "Mixed Negative"
        else:
            return "Mixed Positive"

    else:
        if rating >= 4:
            return "Positive"
        elif rating <= 2:
            return "Negative"
        else:
            return "Neutral"


def sentiment_bucket(score):
    if score >= 0.5:
        return "0.5 to 1.0"
    elif 0.0 <= score < 0.5:
        return "0.0 to 0.49"
    elif -0.5 <= score < 0.0:
        return "-0.49 to 0.0"
    else:
        return "-1.0 to -0.5"


def main():

    engine = create_engine(
        "mssql+pyodbc://FUSION-00\\SQLEXPRESS/PortfolioProject_MarketingAnalytics"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )

    try:

        # 🔥 UPDATED QUERY WITH PRODUCT NAME
        query = """
        SELECT 
            r.ReviewID,
            r.CustomerID,
            r.ProductID,
            p.ProductName,
            r.ReviewDate,
            r.Rating,
            r.ReviewText
        FROM customer_reviews r
        LEFT JOIN products p
            ON r.ProductID = p.ProductID
        """

        customer_reviews_df = pd.read_sql(query, engine)

        print("Data loaded successfully. Shape:", customer_reviews_df.shape)

        sia = SentimentIntensityAnalyzer()

        # Sentiment score
        customer_reviews_df["SentimentScore"] = (
            customer_reviews_df["ReviewText"]
            .apply(lambda x: calculate_sentiment(x, sia))
        )

        # Sentiment category
        customer_reviews_df["SentimentCategory"] = [
            categorize_sentiment(score, rating)
            for score, rating in zip(
                customer_reviews_df["SentimentScore"],
                customer_reviews_df["Rating"]
            )
        ]

        # Sentiment bucket
        customer_reviews_df["SentimentBucket"] = (
            customer_reviews_df["SentimentScore"]
            .apply(sentiment_bucket)
        )

        # Save enriched dataset
        customer_reviews_df.to_csv(
            "fact_customer_reviews_with_sentiment.csv",
            index=False
        )

        print("Sentiment enrichment completed successfully.")

    finally:
        engine.dispose()
        print("Database connection closed.")


if __name__ == "__main__":
    main()