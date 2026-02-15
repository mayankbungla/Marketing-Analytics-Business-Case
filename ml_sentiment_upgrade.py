# !pip install scikit-learn transformers torch matplotlib seaborn

# ==========================================================
# ShopEasy - ML & NLP Enhancement Notebook
# ----------------------------------------------------------
# Goal:
# Extend the existing BI dashboard with predictive modeling.
#
# We will:
# 1. Predict whether a review will receive a high rating (>=4)
# 2. Use structured + text features
# 3. Compare multiple ML models
# 4. Use cross-validation for reliability
# 5. Compare VADER vs Transformer sentiment
# ==========================================================


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from transformers import pipeline

sns.set_style("whitegrid")



# -------------------------------
# Load Dataset
# -------------------------------

df = pd.read_csv("fact_customer_reviews_with_sentiment.csv")

print("Dataset loaded.")
print(df.head())

# Target variable:
# 1 = High Rating (4 or 5)
# 0 = Low Rating (1, 2, 3)

df["HighRating"] = (df["Rating"] >= 4).astype(int)

# Additional engineered features
df["ReviewLength"] = df["ReviewText"].astype(str).apply(len)
df["WordCount"] = df["ReviewText"].astype(str).apply(lambda x: len(x.split()))

df[["SentimentScore", "ReviewLength", "WordCount", "HighRating"]].head()

