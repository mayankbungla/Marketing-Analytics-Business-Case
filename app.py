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
# DATA LOADING LAYER (CACHED FOR PERFORMANCE)
# ==========================================================

DATA_PATH = Path("outputs")

@st.cache_data
def load_data():
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
# RISK ALERT SYSTEM
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

# Determine dominant issue
top_issue = None
if not issue_counts.empty:
    first_issue = issue_counts.iloc[0]["Issue Category"]
    if first_issue != "No Issue Detected":
        top_issue = first_issue

# ==========================================================
# SECTION 4 — STRATEGIC BUSINESS RECOMMENDATIONS
# ==========================================================

st.header("🧠 Strategic Business Recommendations")

# ----------------------------------------------------------
# FULL GROWTH PLAYBOOK (ALL PRODUCTS PRESERVED)
# ----------------------------------------------------------

if st.button("🚀 Reveal Growth & Scaling Strategies"):
    st.subheader(f"Growth Playbook for: {selected_product}")

    growth_playbook = {
        "Climbing Rope": [
            "**Summit Socials:** Launch milestone tagging campaigns.",
            "**Adventure Bundling:** Partner with climbing gyms.",
            "**Safety Authority:** Host safety education streams."
        ],
        "Basketball": [
            "**Streetball Sponsorship:** Sponsor 3v3 tournaments.",
            "**Bulk Pricing for Coaches:** Introduce school pricing tiers.",
            "**Viral Campaign:** Launch trick-shot challenges."
        ],
        "Ski Boots": [
            "**Free Fit Trials:** Partner with ski resorts.",
            "**Athlete Sponsorship:** Promote durability.",
            "**Early Bird Discount:** Seasonal pre-orders."
        ],
        "Ice Skates": [
            "**Rink Partnerships:** Official skate branding.",
            "**Performance Clinics:** Host skating sessions.",
            "**Upgrade Program:** Beginner-to-Pro transition."
        ],
        "Kayak": [
            "**Eco Campaigns:** River cleanups.",
            "**Demo Popups:** Weekend lake trials.",
            "**Accessory Bundles:** Roof rack combo offers."
        ],
        "Football Helmet": [
            "**Safety Campaign:** Youth fitting seminars.",
            "**Bulk Customization:** Logo decals.",
            "**Tech Marketing:** Highlight impact absorption."
        ],
        "Swim Goggles": [
            "**No-Fog Guarantee:** 90-day promise.",
            "**Swim School Partnerships:** Starter kits.",
            "**Bundle Strategy:** Cap + shampoo combo."
        ],
        "Cycling Helmet": [
            "**Commuter Targeting:** Urban safety ads.",
            "**Retail Partnerships:** QR code kiosks.",
            "**Limited Edition Line:** High visibility colors."
        ],
        "Fitness Tracker": [
            "**Corporate Health Programs:** HR deals.",
            "**Influencer Reviews:** Endurance testing.",
            "**App Leaderboard Rewards:** Accessory discounts."
        ],
        "Tennis Racket": [
            "**Demo Events:** Local club trials.",
            "**Free Stringing Service:** Add value.",
            "**Youth Camp Sponsorship:** Brand visibility."
        ],
        "Running Shoes": [
            "**Run Club Sponsorship:** Community engagement.",
            "**Marathon Booths:** Trial experiences.",
            "**Mileage Rewards:** Repeat purchase triggers."
        ],
        "Golf Clubs": [
            "**Driving Range Demos:** Test experiences.",
            "**Coaching Bundles:** Include lessons.",
            "**Virtual Fitting:** Online consultation."
        ],
        "Yoga Mat": [
            "**Studio Affiliate Program:** Commission model.",
            "**Eco Branding:** Sustainability focus.",
            "**Outdoor Events:** Free community sessions."
        ],
        "Dumbbells": [
            "**Workout Guides:** QR unlock content.",
            "**Upgrade Discount:** Weight progression.",
            "**Apartment Targeting:** Compact design marketing."
        ],
        "Baseball Glove": [
            "**Premium Break-In Service:** Value add.",
            "**Youth League Sponsorship:** Opening day visibility.",
            "**Custom Stitching:** Personalization offer."
        ],
        "Volleyball": [
            "**Beach Tournament Branding:** Official ball status.",
            "**Club Bulk Pricing:** Team deals.",
            "**Skill Tutorials:** YouTube SEO strategy."
        ],
        "Surfboard": [
            "**Surf School Leasing:** Brand visibility.",
            "**Designer Storytelling:** Technical differentiation.",
            "**Eco Bundle:** Organic wax inclusion."
        ],
        "Soccer Ball": [
            "**Freestyle Contest:** Instagram engagement.",
            "**Futsal Version:** Low bounce edition.",
            "**Performance Ads:** High-speed flight shots."
        ],
        "Boxing Gloves": [
            "**Starter Kits:** Bundle hand wraps.",
            "**Gym Partnerships:** Replace house gloves.",
            "**Durability Videos:** Stress tests."
        ],
        "Hockey Stick": [
            "**Trial Nights:** Public skate demos.",
            "**Grip Tape Add-On:** Upsell accessory.",
            "**Flex Calculator Tool:** Personalization."
        ]
    }

    strategies = growth_playbook.get(selected_product, [
        "**UGC Ads:** Turn 5-star reviews into video ads.",
        "**Loyalty Rewards:** Early access perks.",
        "**Referral Program:** Give 15%, Get 15%."
    ])

    for s in strategies:
        st.write(f"📈 {s}")

    st.markdown("---")

# ==========================================================
# ROOT CAUSE REMEDIATION — FULL DICTIONARY PRESERVED
# ==========================================================

actual_issues = issue_counts[
    issue_counts["Issue Category"] != "No Issue Detected"
]

top_two_issues = actual_issues.head(2)["Issue Category"].tolist()

recommendations = {
    "Delivery Issue": [
        "**Ship Faster:** Dispatch within 12 hours.",
        "**Courier Optimization:** Improve carrier selection.",
        "**Real-Time Tracking:** SMS notifications.",
        "**Compensation Policy:** Automatic discount for delays."
    ],
    "Product Quality": [
        "**Batch Audit:** Inspect recent production.",
        "**Factory Escalation:** Feedback loop to manufacturer.",
        "**Extended Warranty:** 6-month guarantee.",
        "**Material Upgrade:** Improve durability."
    ],
    "Pricing Issue": [
        "**Bundle Offers:** Add high-margin accessories.",
        "**Competitive Review:** Weekly pricing check.",
        "**Installment Plans:** Reduce upfront barrier.",
        "**Value Communication:** Highlight premium features."
    ],
    "Customer Service": [
        "**4-Hour SLA:** Faster response time.",
        "**Chatbot Automation:** FAQ handling.",
        "**Executive Escalation:** Manager outreach.",
        "**Follow-Up Email:** Post-purchase care."
    ],
    "Packaging Issue": [
        "**Reinforced Packaging:** Reduce damages.",
        "**Premium Unboxing:** Improve experience.",
        "**Eco Materials:** Sustainable + sturdy.",
        "**Easy-Open Design:** Frustration-free."
    ],
    "Performance Issue": [
        "**Instructional Videos:** Prevent misuse.",
        "**Internal Testing:** Stress validation.",
        "**Firmware Update:** Fix known issues.",
        "**Expert Guides:** Weekly best practices."
    ],
    "Usability Issue": [
        "**Simplified Manual:** 3-step clarity.",
        "**QR Video Guide:** Easy access support.",
        "**Quick Start Card:** Immediate clarity.",
        "**Community Forum:** Peer assistance."
    ],
    "Expectation Gap": [
        "**Real Photos:** Authentic visuals.",
        "**Clear Size Guide:** Context images.",
        "**Honest Positioning:** Set correct expectations.",
        "**Comparison Table:** Model differences."
    ]
}

if top_two_issues:
    st.subheader("🚩 Action Plan for Top Improvements")

    for issue in top_two_issues:
        if issue in recommendations:
            with st.expander(f"Immediate Steps for: {issue}", expanded=True):
                for r in recommendations[issue]:
                    st.write(f"• {r}")
else:
    st.success("✅ This product is a top performer! No major issues were detected in the data.")

# ==========================================================
# SECTION 5 — EXECUTIVE SUMMARY + PDF EXPORT
# ==========================================================

st.header("🤖 Executive Summary")

if st.button("Generate Executive Report"):

    summary_display = f"""
### 📦 Product Overview

Product: {selected_product}
Total Reviews: {total_reviews}
Positive Reviews: {positive_reviews}
Negative Reviews: {negative_reviews}

Positive %: {positive_pct:.2f}%
Negative %: {negative_pct:.2f}%

Dominant Issue: {top_issue if top_issue else "None"}
Overall Performance: {"Underperforming" if health_score < 10 else "Strong"}
"""

    st.markdown(summary_display)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Product Intelligence Executive Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph(summary_display.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(elements)

    st.download_button(
        label="📄 Download Executive Report (PDF)",
        data=buffer.getvalue(),
        file_name=f"{selected_product}_Executive_Report.pdf",
        mime="application/pdf"
    )

# ==========================================================
# SECTION 6 — QUALITATIVE INSIGHT
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