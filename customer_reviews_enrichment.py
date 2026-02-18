# ==========================================================
# ShopEasy - Predicting High Customer Ratings
# ----------------------------------------------------------
# Purpose:
# We move beyond descriptive analytics and try to predict
# whether a customer review will receive a high rating (>=4).
#
# We use:
# - Sentiment score (emotional signal)
# - Review length (engagement signal)
# - Word count (verbosity signal)
# - TF-IDF text features (actual words used)
#
# We compare multiple ML models and use cross-validation
# to ensure reliability.
# ==========================================================


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer


# ----------------------------------------------------------
# Step 1: Load Enriched Dataset
# ----------------------------------------------------------
# This dataset already contains SentimentScore from VADER

df = pd.read_csv("fact_customer_reviews_with_sentiment.csv")

print("Dataset Loaded")
print(df.head())


# ----------------------------------------------------------
# Step 2: Create Target Variable
# ----------------------------------------------------------
# 1 = High Rating (4 or 5)
# 0 = Low Rating (1,2,3)

df["HighRating"] = (df["Rating"] >= 4).astype(int)


# ----------------------------------------------------------
# Step 3: Feature Engineering
# ----------------------------------------------------------
# We create additional behavioral features

df["ReviewLength"] = df["ReviewText"].astype(str).apply(len)
df["WordCount"] = df["ReviewText"].astype(str).apply(lambda x: len(x.split()))
df["AbsSentiment"] = df["SentimentScore"].abs()

# Features used for modeling
numeric_features = [
    "SentimentScore",
    "AbsSentiment",
    "ReviewLength",
    "WordCount"
]

text_feature = "ReviewText"

X = df[numeric_features + [text_feature]]
y = df["HighRating"]


# ----------------------------------------------------------
# Step 4: Train/Test Split
# ----------------------------------------------------------
# We separate data so we can test on unseen examples

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# ----------------------------------------------------------
# Step 5: Preprocessing
# ----------------------------------------------------------
# Numeric features → scaled
# Text feature → TF-IDF transformation

numeric_transformer = StandardScaler()

text_transformer = TfidfVectorizer(
    max_features=4000,
    stop_words="english",
    ngram_range=(1,2)
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("text", text_transformer, text_feature)
    ]
)


# ----------------------------------------------------------
# Step 6: Logistic Regression Model
# ----------------------------------------------------------

log_model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])

log_model.fit(X_train, y_train)

log_preds = log_model.predict(X_test)
log_probs = log_model.predict_proba(X_test)[:, 1]

print("\nLogistic Regression Results")
print("ROC-AUC:", roc_auc_score(y_test, log_probs))
print(classification_report(y_test, log_preds))


# ----------------------------------------------------------
# Step 7: Random Forest Model
# ----------------------------------------------------------

rf_model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=300,
        random_state=42
    ))
])

rf_model.fit(X_train, y_train)

