# !pip install scikit-learn transformers torch matplotlib seaborn

# ML & Transformer Upgrade
# Extends sentiment project with predictive modeling and model comparison

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

from transformers import pipeline


# -------------------------------
# Load Dataset
# -------------------------------

df = pd.read_csv("fact_customer_reviews_with_sentiment.csv")

print("Dataset loaded.")
print(df.head())

# Target
df["HighRating"] = (df["Rating"] >= 4).astype(int)

# Additional numeric features
df["ReviewLength"] = df["ReviewText"].astype(str).apply(len)
df["WordCount"] = df["ReviewText"].astype(str).apply(lambda x: len(x.split()))

df[["SentimentScore", "ReviewLength", "WordCount", "HighRating"]].head()
