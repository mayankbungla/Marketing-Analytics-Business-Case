# pip install pandas numpy scikit-learn transformers torch matplotlib seaborn

# ==========================================================
# ShopEasy - End-to-End ML & NLP Enhancement
# ----------------------------------------------------------
# Objective:
# Predict whether a customer review will receive a high rating (>=4)
# using structured features and text features.
#
# This notebook includes:
# - EDA
# - Feature Engineering
# - Multiple ML models
# - Cross-validation
# - Hyperparameter tuning
# - Model evaluation
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

sns.set_style("whitegrid")

df = pd.read_csv("fact_customer_reviews_with_sentiment.csv")

print("Shape:", df.shape)
df.head()

# Distribution of ratings
sns.countplot(x="Rating", data=df)
plt.title("Rating Distribution")
plt.show()

# Distribution of sentiment score
sns.histplot(df["SentimentScore"], kde=True)
plt.title("Sentiment Score Distribution")
plt.show()

# Correlation check
df["HighRating"] = (df["Rating"] >= 4).astype(int)
print(df[["SentimentScore", "Rating", "HighRating"]].corr())


df["ReviewLength"] = df["ReviewText"].astype(str).apply(len)
df["WordCount"] = df["ReviewText"].astype(str).apply(lambda x: len(x.split()))
df["AbsSentiment"] = df["SentimentScore"].abs()

numeric_features = [
    "SentimentScore",
    "AbsSentiment",
    "ReviewLength",
    "WordCount"
]

text_feature = "ReviewText"

X = df[numeric_features + [text_feature]]
y = df["HighRating"]
