# pip install pandas numpy scikit-learn transformers torch matplotlib seaborn

# ==========================================================
# ShopEasy ML & NLP Enhancement
# ----------------------------------------------------------
# Purpose:
# Move from descriptive analytics to predictive modeling.
# We want to predict whether a review will receive a high rating.
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from transformers import pipeline

sns.set_style("whitegrid")

# Load the dataset
df = pd.read_csv("fact_customer_reviews_with_sentiment.csv")

print("Dataset shape:", df.shape)
df.head()

# Target variable
df["HighRating"] = (df["Rating"] >= 4).astype(int)

# Text-based features
df["ReviewLength"] = df["ReviewText"].astype(str).apply(len)
df["WordCount"] = df["ReviewText"].astype(str).apply(lambda x: len(x.split()))

# Emotional intensity feature
df["AbsSentiment"] = df["SentimentScore"].abs()

# Rating deviation (how extreme rating is)
df["RatingDeviation"] = abs(df["Rating"] - 3)

df[["SentimentScore", "AbsSentiment", "ReviewLength", 
    "WordCount", "RatingDeviation", "HighRating"]].head()
