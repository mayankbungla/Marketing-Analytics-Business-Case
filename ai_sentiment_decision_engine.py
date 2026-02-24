# ==========================================================
# AI-ENHANCED PRODUCT REVIEW INTELLIGENCE DASHBOARD
# Enterprise Sentiment Intelligence & AI Decision Support
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import google.generativeai as genai
import io
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="AI Product Intelligence System",
    layout="wide"
)

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
# GEMINI CONFIGURATION
# ==========================================================

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

# ==========================================================
# SAFE AI GENERATION (CACHED + FALLBACK)
# ==========================================================

@st.cache_data(show_spinner=False)
def generate_ai(prompt):
    if not AI_AVAILABLE:
        return None
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return None

# ==========================================================
# DATA LOADING
# ==========================================================

DATA_PATH = Path("outputs")

@st.cache_data
def load_data():
    review_files = sorted(DATA_PATH.glob("review_intelligence_dataset_*.csv"))
    summary_files = sorted(DATA_PATH.glob("product_summary_*.csv"))

    if not review_files or not summary_files:
        return None, None

    return pd.read_csv(review_files[-1]), pd.read_csv(summary_files[-1])


df, product_summary = load_data()

if df is None:
    st.error("Run review_intelligence_engine.py first.")
    st.stop()

# ==========================================================
# BUSINESS READABILITY TRANSFORMATION
# ==========================================================

product_summary = product_summary.rename(columns={
    "TotalReviews": "Total Reviews",
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

summary_row = product_summary[
    product_summary["ProductName"] == selected_product
].iloc[0]

product_df = df[df["ProductName"] == selected_product]

total_reviews = summary_row["Total Reviews"]
positive_reviews = summary_row["Number of Positive Reviews"]
negative_reviews = summary_row["Number of Negative Reviews"]
positive_pct = summary_row["Positive Review Percentage (%)"]
negative_pct = summary_row["Negative Review Percentage (%)"]
health_score = summary_row["Overall Health Score"]

# ==========================================================
# KPI DISPLAY
# ==========================================================

st.subheader("📌 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("Total Reviews", int(total_reviews))
col2.metric("Positive Reviews", int(positive_reviews), delta=f"{positive_pct:.1f}%")
col3.metric("Negative Reviews", int(negative_reviews), delta=f"{negative_pct:.1f}%")

# ==========================================================
# HEALTH SCORE GAUGE
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
# RISK ALERT
# ==========================================================

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

st.dataframe(issue_counts, use_container_width=True)

# ----------------------------------------------------------
# SECTION 4 — STRATEGIC BUSINESS RECOMMENDATIONS
# ----------------------------------------------------------

st.header("🧠 Strategic Business Recommendations")

if st.button("🚀 Reveal Growth & Scaling Strategies"):

    prompt = f"""
You are a senior growth consultant.

Product: {selected_product}

Generate 5 short, practical growth strategies.
Bullet points only.
No paragraphs.
Business-friendly.
Actionable.
"""

    strategy = generate_ai(prompt)

    if strategy:
        st.markdown(strategy)
    else:
        st.warning("AI strategy temporarily unavailable.")

# ================= AI ACTION PLAN FOR TOP ISSUES =================

actual_issues = issue_counts[issue_counts["Issue Category"] != "No Issue Detected"]
top_two_issues = actual_issues.head(2)["Issue Category"].tolist()

if top_two_issues:
    st.subheader("🚩 Action Plan for Top Improvements")

    prompt = f"""
You are an operations strategist.

Product: {selected_product}
Top Issues: {top_two_issues}

Return STRICT JSON like:

{{
 "Issue Name": ["bullet1", "bullet2", "bullet3"],
 "Issue Name 2": ["bullet1", "bullet2", "bullet3"]
}}

Max 4 bullets per issue.
Concise.
"""

    ai_plan_raw = generate_ai(prompt)

    try:
        ai_plan = json.loads(ai_plan_raw)
    except:
        ai_plan = {}

    for issue in top_two_issues:
        with st.expander(f"Immediate Steps for: {issue}", expanded=True):

            if issue in ai_plan:
                for r in ai_plan[issue]:
                    st.write(f"• {r}")
            else:
                st.write("• Review operational process immediately.")
                st.write("• Assign owner for issue resolution.")
                st.write("• Implement tracking and monitoring.")
else:
    st.success("✅ This product is a top performer! No major issues were detected in the data.")

# ==========================================================
# SECTION 5 — EXECUTIVE SUMMARY
# ==========================================================

st.header("🤖 Executive Summary")

if st.button("Generate Executive Report"):

    prompt = f"""
You are preparing a board-level executive summary.

Product: {selected_product}
Health Score: {health_score}
Positive %: {positive_pct}
Negative %: {negative_pct}

Provide:

Performance Snapshot:
• bullet

Key Risks:
• bullet

Immediate Priority:
• bullet

Growth Outlook:
• bullet

Keep concise.
"""

    executive = generate_ai(prompt)

    if executive:
        st.markdown(executive)
    else:
        st.warning("AI executive summary temporarily unavailable.")

# ==========================================================
# QUALITATIVE INSIGHT
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