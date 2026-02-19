# ==========================================================
# ShopEasy Customer Intelligence System
# ----------------------------------------------------------
# This notebook builds:
# 1. Complaint Topic Modeling
# 2. Dissatisfaction Risk Scoring
# 3. Product-Level Risk Analysis
# 4. Sentiment Trend & Anomaly Detection
# ==========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

sns.set_style("whitegrid")

df = pd.read_csv("fact_customer_reviews_with_sentiment.csv")

df["ReviewDate"] = pd.to_datetime(df["ReviewDate"])

print("Dataset shape:", df.shape)
print(df.head())

#COMPLAINT TOPIC MODELING

vectorizer = TfidfVectorizer(
    max_features=3000,
    stop_words="english",
    ngram_range=(1,2)
)

X_text = vectorizer.fit_transform(df["ReviewText"].astype(str))
lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(X_text)

feature_names = vectorizer.get_feature_names_out()

def print_topics(model, feature_names, n_top_words=10):
    for topic_idx, topic in enumerate(model.components_):
        print(f"\nTopic {topic_idx + 1}:")
        print(", ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))

print_topics(lda, feature_names)
