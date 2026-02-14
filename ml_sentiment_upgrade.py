#!pip install scikit-learn transformers torch matplotlib seaborn
# ML & Transformer Upgrade
# Extends sentiment project with predictive modeling and model comparison

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

from transformers import pipeline
