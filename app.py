# ==========================================================
# PRODUCT REVIEW INTELLIGENCE DASHBOARD
# Enterprise Sentiment Intelligence & Decision Support System
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Product Intelligence System",
    layout="wide"
)

# Custom Dark Theme Styling
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 AI-Powered Product Review Intelligence")


# ==========================================================
# DATA LOADING LAYER (Cached for Performance)
# ==========================================================

DATA_PATH = Path("outputs")

@st.cache_data
def load_data():
    """
    Loads the latest processed review-level and product-level datasets.
    
    """
    review_files = sorted(DATA_PATH.glob("review_intelligence_dataset_*.csv"))
    summary_files = sorted(DATA_PATH.glob("product_summary_*.csv"))

    if not review_files or not summary_files:
        return None, None

    df_reviews = pd.read_csv(review_files[-1])
    df_summary = pd.read_csv(summary_files[-1])

    return df_reviews, df_summary


df, product_summary = load_data()

if df is None or product_summary is None:
    st.error("Processed intelligence files not found. Run review_intelligence_engine.py first.")
    st.stop()


# ==========================================================
# BUSINESS READABILITY TRANSFORMATION
# ==========================================================

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
# SECTION 1 — PRODUCT HEALTH RANKING
# ==========================================================

st.header("🏆 Product Health Ranking")

product_summary = product_summary.sort_values(
    "Overall Health Score",
    ascending=False
)

st.dataframe(product_summary, use_container_width=True)


# ==========================================================
# SECTION 2 — PRODUCT DEEP DIVE
# ==========================================================

st.header("🔍 Product Deep Dive")

selected_product = st.selectbox(
    "Select Product",
    sorted(product_summary["ProductName"].unique())
)

# Retrieve product-level metrics directly from summary table
summary_row = product_summary[
    product_summary["ProductName"] == selected_product
].iloc[0]

total_reviews = summary_row["Total Reviews"]
positive_reviews = summary_row["Number of Positive Reviews"]
negative_reviews = summary_row["Number of Negative Reviews"]
positive_pct = summary_row["Positive Review Percentage (%)"]
negative_pct = summary_row["Negative Review Percentage (%)"]
health_score = summary_row["Overall Health Score"]

# Retrieve review-level data for qualitative breakdown
product_df = df[df["ProductName"] == selected_product]


# ==========================================================
# SECTION 2.1 — KPI DISPLAY
# ==========================================================

st.subheader("📌 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("Total Reviews", int(total_reviews))

col2.metric(
    "Positive Reviews",
    int(positive_reviews),
    delta=f"{positive_pct:.1f}%"
)

col3.metric(
    "Negative Reviews",
    int(negative_reviews),
    delta=f"{negative_pct:.1f}%"
)


# ==========================================================
# SECTION 2.2 — HEALTH SCORE GAUGE
# ==========================================================

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


# ==========================================================
# SECTION 2.3 — RISK ALERT SYSTEM
# ==========================================================

if negative_pct > 40:
    st.error("🚨 Critical Risk: High negative sentiment detected.")
elif negative_pct > 25:
    st.warning("⚠️ Moderate Risk: Rising negative sentiment.")
else:
    st.success("✅ Product health stable.")


# ==========================================================
# SECTION 3 — ROOT CAUSE ANALYSIS
# ==========================================================

st.subheader("📌 Complaint Distribution")

issue_counts = (
    product_df["DetectedIssue"]
    .value_counts()
    .reset_index()
)

issue_counts.columns = ["Issue Category", "Number of Reviews"]

st.dataframe(issue_counts, use_container_width=True)


# ==========================================================
# SECTION 4 — RULE-BASED BUSINESS RECOMMENDATIONS
# ==========================================================

st.header("🧠 AI Business Recommendations")

top_issue = issue_counts.iloc[0]["Issue Category"] if not issue_counts.empty else None

recommendations = {
    "Product Quality": [
        "Enhance quality control inspections.",
        "Collaborate with suppliers to improve material standards.",
        "Introduce extended warranty programs."
    ],
    "Delivery Issue": [
        "Optimize last-mile logistics routes.",
        "Partner with higher SLA courier services.",
        "Offer priority shipping options."
    ],
    "Pricing Issue": [
        "Re-evaluate pricing strategy against competitors.",
        "Launch targeted promotional campaigns."
    ],
    "Customer Service": [
        "Improve support team training.",
        "Implement stricter response time KPIs."
    ]
}

if top_issue in recommendations:
    for rec in recommendations[top_issue]:
        st.write("•", rec)
else:
    st.write("• Maintain current performance and leverage positive reviews in marketing.")


# ==========================================================
# SECTION 5 — EXECUTIVE SUMMARY + PDF EXPORT
# ==========================================================

st.header("🤖 Executive Summary")

if st.button("Generate Executive Report"):

    # ----------------------------
    # Streamlit Display Version
    # ----------------------------

    summary_display = f"""
### 📦 Product Overview

**Product:** {selected_product}  
**Total Reviews:** {total_reviews}  
**Positive Reviews:** {positive_reviews}  
**Negative Reviews:** {negative_reviews}  

**Positive Review Percentage:** {positive_pct:.2f}%  
**Negative Review Percentage:** {negative_pct:.2f}%  

---

**Dominant Issue:** {top_issue if top_issue else "None"}  
**Overall Performance:** {"Underperforming" if health_score < 10 else "Strong"}
"""

    st.markdown(summary_display)

    # ----------------------------
    # PDF Generation Layer
    # ----------------------------

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Product Intelligence Executive Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph("Product Overview", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Product:</b> {selected_product}", styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Total Reviews:</b> {total_reviews}", styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Positive Reviews:</b> {positive_reviews}", styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Negative Reviews:</b> {negative_reviews}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Positive Review Percentage:</b> {positive_pct:.2f}%", styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(f"<b>Negative Review Percentage:</b> {negative_pct:.2f}%", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Performance Summary", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Dominant Issue:</b> {top_issue if top_issue else 'None'}", styles["Normal"]))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(
        f"<b>Overall Performance:</b> {'Underperforming' if health_score < 10 else 'Strong'}",
        styles["Normal"]
    ))

    doc.build(elements)

    st.download_button(
        label="📄 Download Executive Report (PDF)",
        data=buffer.getvalue(),
        file_name=f"{selected_product}_Executive_Report.pdf",
        mime="application/pdf"
    )


# ==========================================================
# SECTION 6 — QUALITATIVE INSIGHT LAYER
# ==========================================================

st.header("🔥 Top 5 Positive Reviews")

st.dataframe(
    product_df.sort_values("SentimentScore", ascending=False)
    .head(5)[["ReviewText", "SentimentScore"]],
    use_container_width=True
)

st.header("⚠️ Top 5 Negative Reviews")

st.dataframe(
    product_df.sort_values("SentimentScore")
    .head(5)[["ReviewText", "SentimentScore"]],
    use_container_width=True
)