# pip install nltk pandas sqlalchemy pyodbc

import pandas as pd
from sqlalchemy import create_engine
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer # model designed for analyzing text like reviews or comments


# -------------------------------
# Download VADER lexicon )
# -------------------------------
nltk.download("vader_lexicon", quiet=True)


def calculate_sentiment(text, analyzer):
    """
    Calculate compound sentiment score using VADER.
    Returns value between -1 and 1.
    """
    text = str(text)  # handle nulls safely
    score = analyzer.polarity_scores(text)
    return score["compound"]


def categorize_sentiment(score, rating):
    """
    Combine text sentiment with star rating.
    """
    rating = 0 if pd.isna(rating) else rating  # If rating ever becomes null in future data loads, pipeline won’t crash

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
    """Bucket sentiment score into readable ranges."""
    if score >= 0.5:
        return "0.5 to 1.0"
    elif 0.0 <= score < 0.5:
        return "0.0 to 0.49"
    elif -0.5 <= score < 0.0:
        return "-0.49 to 0.0"
    else:
        return "-1.0 to -0.5"


def main():
    # -------------------------------
    # Connect to SQL Server
    # -------------------------------
    engine = create_engine(
        "mssql+pyodbc://FUSION-00\\SQLEXPRESS/PortfolioProject_MarketingAnalytics"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )

    try:
        # -------------------------------
        # Load data
        # -------------------------------
        query = """
        SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText 
        FROM customer_reviews
        """

        customer_reviews_df = pd.read_sql(query, engine)

        print("Data loaded successfully. Shape:", customer_reviews_df.shape)
        print(customer_reviews_df.head())

        # -------------------------------
        # Initialize Sentiment Analyzer
        # -------------------------------
        sia = SentimentIntensityAnalyzer()

        # -------------------------------
        # Apply Sentiment Logic
        # -------------------------------

        # Sentiment score
        customer_reviews_df["SentimentScore"] = (
            customer_reviews_df["ReviewText"]
            .apply(lambda x: calculate_sentiment(x, sia))
        )

        # Sentiment category
        customer_reviews_df["SentimentCategory"] = [
            categorize_sentiment(score, rating)
            for score, rating in zip(customer_reviews_df["SentimentScore"], customer_reviews_df["Rating"])
        ]

        # Sentiment bucket
        customer_reviews_df["SentimentBucket"] = (
            customer_reviews_df["SentimentScore"].apply(sentiment_bucket)
        )

        print(customer_reviews_df.head())

        # -------------------------------
        # Save to CSV
        # -------------------------------
        customer_reviews_df.to_csv(
            "fact_customer_reviews_with_sentiment.csv",
            index=False
        )

        print("Sentiment enrichment completed successfully.")

    finally:
        # Proper cleanup 
        engine.dispose()
        print("Database connection closed.")


# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    main()