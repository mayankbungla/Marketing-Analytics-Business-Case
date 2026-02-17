# pip install nltk pandas sqlalchemy pyodbc

import pandas as pd
from sqlalchemy import create_engine
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")


# -------------------------------
# Connect to SQL Server
# -------------------------------

engine = create_engine(
    "mssql+pyodbc://FUSION-00\\SQLEXPRESS/PortfolioProject_MarketingAnalytics"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

query = """
SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText 
FROM customer_reviews
"""

customer_reviews_df = pd.read_sql(query, engine)


# -------------------------------
# Initialize Sentiment Analyzer
# -------------------------------

sia = SentimentIntensityAnalyzer()


# Calculate compound sentiment score
def calculate_sentiment(text):
    # Convert to string in case of nulls
    text = str(text)
    score = sia.polarity_scores(text)
    return score["compound"]


# Categorize sentiment using both text score and rating
def categorize_sentiment(score, rating):

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


# Bucket sentiment score into readable ranges
def sentiment_bucket(score):

    if score >= 0.5:
        return "0.5 to 1.0"
    elif 0.0 <= score < 0.5:
        return "0.0 to 0.49"
    elif -0.5 <= score < 0.0:
        return "-0.49 to 0.0"
    else:
        return "-1.0 to -0.5"


# ------------------------------
# Apply Sentiment Logic
# ------------------------------

# Sentiment score
customer_reviews_df["SentimentScore"] = (
    customer_reviews_df["ReviewText"].apply(calculate_sentiment)
)

# Sentiment category (using score + rating)
customer_reviews_df["SentimentCategory"] = [
    categorize_sentiment(score, rating)
    for score, rating in zip(
        customer_reviews_df["SentimentScore"],
        customer_reviews_df["Rating"]
    )
]

# Sentiment bucket
customer_reviews_df["SentimentBucket"] = (
    customer_reviews_df["SentimentScore"].apply(sentiment_bucket)
)


print(customer_reviews_df.head())

# Save final dataset =
customer_reviews_df.to_csv(
    "fact_customer_reviews_with_sentiment.csv",
    index=False
)

print("Sentiment enrichment completed successfully.")
