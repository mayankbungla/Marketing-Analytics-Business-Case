import streamlit as st
import pandas as pd
from pathlib import Path

st.title("Debug Mode")

st.write("App started successfully.")

DATA_PATH = Path("outputs")

st.write("Checking outputs folder exists:", DATA_PATH.exists())

st.write("Listing files in outputs folder:")
st.write(list(DATA_PATH.glob("*")))

if DATA_PATH.exists():
    review_files = sorted(DATA_PATH.glob("review_intelligence_dataset_*.csv"))
    summary_files = sorted(DATA_PATH.glob("product_summary_*.csv"))

    st.write("Review files found:", review_files)
    st.write("Summary files found:", summary_files)

    if review_files:
        df = pd.read_csv(review_files[-1])
        st.write("Loaded review dataset successfully.")
        st.write(df.head())

    if summary_files:
        summary = pd.read_csv(summary_files[-1])
        st.write("Loaded summary dataset successfully.")
        st.write(summary.head())