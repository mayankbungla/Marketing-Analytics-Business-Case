# pip install nltk pandas sqlalchemy pyodbc

import pandas as pd 
from sqlalchemy import create_engine    
import nltk
# a ready-made sentiment model built into NLTK, designed for analyzing text like reviews or comments
from nltk.sentiment.vader import SentimentIntensityAnalyzer   

nltk.download('vader_lexicon')


#  Connect to SQL Server and load data
engine = create_engine(
    "mssql+pyodbc://FUSION-00\\SQLEXPRESS/PortfolioProject_MarketingAnalytics"
    "?driver=SQL+Server&trusted_connection=yes"
)
query = """SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText FROM customer_reviews"""
customer_reviews_df = pd.read_sql(query, engine)

# Initialize the VADER sentiment intensity analyzer
sia = SentimentIntensityAnalyzer()

# Define a function to calculate sentiment scores of review text using VADER and
# Return the compound score, which is a normalized score between -1 (most negative) and 1 (most positive)
def calculate_sentiment(review):
    sentiment = sia.polarity_scores(review)
    return sentiment['compound']    

# Define a function to categorize sentiment using both the sentiment score and the review rating
def categorize_sentiment(score, rating):
    if score > 0.05:                     # Positive sentiment score
        if rating >= 4:
            return 'Positive'            # High rating and positive sentiment
        elif rating == 3:
            return 'Mixed Positive'      # Neutral rating but positive sentiment
        else:
            return 'Mixed Negative'      # Low rating but positive sentiment
    elif score < -0.05:                  # Negative sentiment score
        if rating <= 2:
            return 'Negative'            # Low rating and negative sentiment
        elif rating == 3:
            return 'Mixed Negative'      # Neutral rating but negative sentiment
        else:
            return 'Mixed Positive'      # High rating but negative sentiment
    else:                                # Neutral sentiment score
        if rating >= 4:
            return 'Positive'            # High rating with neutral sentiment
        elif rating <= 2:
            return 'Negative'            # Low rating with neutral sentiment
        else:
            return 'Neutral'             # Neutral rating and neutral sentiment

# Define a function to bucket sentiment scores into text ranges
def sentiment_bucket(score):
    if score >= 0.5:
        return '0.5 to 1.0'  # Strongly positive sentiment
    elif 0.0 <= score < 0.5:
        return '0.0 to 0.49'  # Mildly positive sentiment
    elif -0.5 <= score < 0.0:
        return '-0.49 to 0.0'  # Mildly negative sentiment
    else:
        return '-1.0 to -0.5'  # Strongly negative sentiment

# Apply sentiment analysis to calculate sentiment scores for each review
customer_reviews_df['SentimentScore'] = customer_reviews_df['ReviewText'].apply(calculate_sentiment)

# Apply sentiment categorization using both text and rating
customer_reviews_df['SentimentCategory'] = customer_reviews_df.apply(
    lambda row: categorize_sentiment(row['SentimentScore'], row['Rating']), axis=1)

# Apply sentiment bucketing to categorize scores into defined ranges
customer_reviews_df['SentimentBucket'] = customer_reviews_df['SentimentScore'].apply(sentiment_bucket)

print(customer_reviews_df.head())
customer_reviews_df.to_csv('fact_customer_reviews_with_sentiment.csv', index=False)