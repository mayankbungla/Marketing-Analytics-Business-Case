# ==========================================================
# PRODUCT REVIEW INTELLIGENCE DASHBOARD
# Enterprise-Style Sentiment Intelligence System
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import SimpleDocTemplate
import io

# ----------------------------------------------------------
# Page Configuration
# ----------------------------------------------------------

st.set_page_config(page_title="Product Intelligence System", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI-Powered Product Review Intelligence")

# ----------------------------------------------------------
# Load Data
# ----------------------------------------------------------

DATA_PATH = Path("outputs")
review_files = sorted(DATA_PATH.glob("review_intelligence_dataset_*.csv"))
summary_files = sorted(DATA_PATH.glob("product_summary_*.csv"))

if not review_files or not summary_files:
    st.error("Run intelligence engine first.")
    st.stop()

df = pd.read_csv(review_files[-1])
product_summary = pd.read_csv(summary_files[-1])

if "ProductName" not in df.columns:
    st.error("ProductName column missing.")
    st.stop()

product_summary = product_summary.rename(columns={
    "TotalReviews": "Total Reviews",
    "AvgSentiment": "Average Sentiment Score",
    "NegativeReviews": "Number of Negative Reviews",
    "PositiveReviews": "Number of Positive Reviews",
    "NegativePct": "Negative Review Percentage (%)",
    "PositivePct": "Positive Review Percentage (%)",
    "HealthScore": "Overall Health Score"
})

# ==========================================================
# SECTION 1 — HEALTH RANKING
# ==========================================================

st.header("🏆 Product Health Ranking")
product_summary = product_summary.sort_values("Overall Health Score", ascending=False)
st.dataframe(product_summary)

# ==========================================================
# SECTION 2 — PRODUCT DEEP DIVE
# ==========================================================

st.header("🔍 Product Deep Dive")

selected_product = st.selectbox(
    "Select Product",
    sorted(df["ProductName"].unique())
)

product_df = df[df["ProductName"] == selected_product]

total_reviews = len(product_df)
positive_reviews = (product_df["SentimentScore"] > 0.05).sum()
negative_reviews = (product_df["SentimentScore"] < -0.05).sum()
negative_pct = (negative_reviews / total_reviews * 100) if total_reviews > 0 else 0

health_score = product_summary.loc[
    product_summary["ProductName"] == selected_product,
    "Overall Health Score"
].values[0]

# ----------------------------------------------------------
# Key Performance Indicators 
# ----------------------------------------------------------

st.subheader("📌 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Total Reviews",
    value=total_reviews
)

col2.metric(
    label="Positive Reviews",
    value=positive_reviews,
    delta=f"{(positive_reviews/total_reviews*100):.1f}%" if total_reviews > 0 else "0%"
)

col3.metric(
    label="Negative Reviews",
    value=negative_reviews,
    delta=f"{negative_pct:.1f}%"
)

# ----------------------------------------------------------
# Health Score Gauge Meter
# ----------------------------------------------------------

st.subheader("🎯 Overall Health Score Gauge")

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=health_score,
    title={'text': "Health Score"},
    gauge={
        'axis': {'range': [-100, 100]},
        'bar': {'color': "white"},
        'steps': [
            {'range': [-100, -20], 'color': "red"},
            {'range': [-20, 20], 'color': "orange"},
            {'range': [20, 100], 'color': "green"}
        ]
    }
))

fig_gauge.update_layout(template="plotly_dark")
st.plotly_chart(fig_gauge, use_container_width=True)

# ----------------------------------------------------------
# Alert System
# ----------------------------------------------------------

if negative_pct > 40:
    st.error("🚨 Critical Risk: High negative sentiment detected.")
elif negative_pct > 25:
    st.warning("⚠️ Moderate Risk: Rising negative sentiment.")
else:
    st.success("✅ Product health stable.")

# ==========================================================
# ROOT CAUSE ANALYSIS
# ==========================================================

st.subheader("📌 Complaint Distribution")

issue_counts = (
    product_df["DetectedIssue"]
    .value_counts()
    .reset_index()
)

issue_counts.columns = ["Issue Category", "Number of Reviews"]

st.dataframe(issue_counts)

# ==========================================================
# SMART RECOMMENDATIONS
# ==========================================================

st.header("🧠 AI Business Recommendations")

top_issue = issue_counts.iloc[0]["Issue Category"] if not issue_counts.empty else None

recommendations = []

if top_issue == "Product Quality":
    recommendations += [
        "Enhance quality control inspections.",
        "Work with suppliers to improve materials.",
        "Offer replacement guarantee to build trust."
    ]
elif top_issue == "Delivery Issue":
    recommendations += [
        "Optimize logistics routes.",
        "Partner with faster courier services.",
        "Introduce priority shipping options."
    ]
elif top_issue == "Pricing Issue":
    recommendations += [
        "Run targeted discount campaigns.",
        "Adjust pricing strategy based on competitor analysis."
    ]
elif top_issue == "Customer Service":
    recommendations += [
        "Improve customer support training.",
        "Implement response time KPIs."
    ]
else:
    recommendations.append("Maintain performance and leverage positive reviews.")

for rec in recommendations:
    st.write("•", rec)

# ==========================================================
# AI EXECUTIVE SUMMARY + PDF EXPORT
# ==========================================================

st.header("🤖 AI Executive Summary")

if st.button("Generate Executive Report"):

    summary_text = f"""
Product: {selected_product}
Total Reviews: {total_reviews}
Positive Reviews: {positive_reviews}
Negative Reviews: {negative_reviews}
Negative Review Percentage: {negative_pct:.2f}%

Dominant Issue: {top_issue if top_issue else "None"}

Overall Performance: {"Underperforming" if negative_reviews > positive_reviews else "Strong"}

Strategic Recommendations:
{chr(10).join(recommendations)}
"""

    st.info(summary_text)

    # ------------------------------------------------------
    # Generate Downloadable PDF
    # ------------------------------------------------------

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Product Intelligence Executive Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(summary_text.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(elements)

    st.download_button(
        label="📄 Download Executive Report (PDF)",
        data=buffer.getvalue(),
        file_name=f"{selected_product}_Executive_Report.pdf",
        mime="application/pdf"
    )

# ==========================================================
# TOP REVIEWS
# ==========================================================

st.header("🔥 Top 5 Positive Reviews")
st.dataframe(product_df.sort_values("SentimentScore", ascending=False).head(5)[["ReviewText", "SentimentScore"]])

st.header("⚠️ Top 5 Negative Reviews")
st.dataframe(product_df.sort_values("SentimentScore").head(5)[["ReviewText", "SentimentScore"]])