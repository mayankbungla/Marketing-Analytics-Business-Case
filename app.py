# ==========================================================
# PRODUCT REVIEW INTELLIGENCE DASHBOARD — UPGRADED v2
# Smarter AI summary | Sidebar nav | Compare mode | Rich charts
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as rl_colors
import io
from groq import Groq

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Product Intelligence System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ---- Base ---- */
.stApp { background-color: #0E1117; color: white; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background-color: #161B22;
    border-right: 1px solid #30363D;
}

/* ---- Metric cards ---- */
div[data-testid="metric-container"] {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 16px;
}

/* ---- Section headers ---- */
h2 { border-bottom: 1px solid #30363D; padding-bottom: 6px; }

/* ---- Compare columns ---- */
.compare-col {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 16px;
    margin: 4px;
}

/* ---- Alert badge ---- */
.badge-good  { background:#1a4731; color:#3fb968; border-radius:6px; padding:4px 10px; font-size:13px; }
.badge-warn  { background:#3d2e00; color:#f5a623; border-radius:6px; padding:4px 10px; font-size:13px; }
.badge-crit  { background:#3d1515; color:#f05252; border-radius:6px; padding:4px 10px; font-size:13px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# DATA LOADING
# ==========================================================

DATA_PATH = Path("outputs")

@st.cache_data
def load_data():
    review_files  = sorted(DATA_PATH.glob("review_intelligence_dataset_*.csv"))
    summary_files = sorted(DATA_PATH.glob("product_summary_*.csv"))
    if not review_files or not summary_files:
        return None, None
    df_reviews  = pd.read_csv(review_files[-1])
    df_summary  = pd.read_csv(summary_files[-1])
    return df_reviews, df_summary

df, product_summary = load_data()

if df is None or product_summary is None:
    st.error("Processed intelligence files not found. Run review_intelligence_engine.py first.")
    st.stop()

# Column rename for readability
product_summary = product_summary.rename(columns={
    "TotalReviews":     "Total Reviews",
    "AvgSentiment":     "Average Sentiment Score",
    "NegativeReviews":  "Number of Negative Reviews",
    "PositiveReviews":  "Number of Positive Reviews",
    "NegativePct":      "Negative Review Percentage (%)",
    "PositivePct":      "Positive Review Percentage (%)",
    "HealthScore":      "Overall Health Score"
})

product_summary = product_summary.sort_values("Overall Health Score", ascending=False)
all_products = sorted(product_summary["ProductName"].unique())

# ==========================================================
# SIDEBAR — NAVIGATION + FILTERS
# ==========================================================

with st.sidebar:
    st.markdown("## 📊 Intelligence Hub")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏆 Product Rankings", "🔍 Deep Dive", "⚔️ Compare Products", "🤖 AI Executive Report"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🎛️ Global Filters")

    min_reviews = st.slider(
        "Min. Reviews",
        min_value=1,
        max_value=int(product_summary["Total Reviews"].max()),
        value=1,
        help="Filter out products with too few reviews"
    )

    health_filter = st.selectbox(
        "Health Status",
        ["All", "Strong (score > 20)", "Moderate (-20 to 20)", "At Risk (score < -20)"]
    )

    st.markdown("---")
    st.caption("ShopEasy · Product Intelligence v2")

# Apply global filters
filtered_summary = product_summary[product_summary["Total Reviews"] >= min_reviews].copy()

if health_filter == "Strong (score > 20)":
    filtered_summary = filtered_summary[filtered_summary["Overall Health Score"] > 20]
elif health_filter == "Moderate (-20 to 20)":
    filtered_summary = filtered_summary[
        (filtered_summary["Overall Health Score"] >= -20) &
        (filtered_summary["Overall Health Score"] <= 20)
    ]
elif health_filter == "At Risk (score < -20)":
    filtered_summary = filtered_summary[filtered_summary["Overall Health Score"] < -20]

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_alert_badge(neg_pct):
    if neg_pct > 40:
        return "🚨 Critical Risk"
    elif neg_pct > 25:
        return "⚠️ Moderate Risk"
    else:
        return "✅ Stable"

def get_summary_row(product_name):
    return product_summary[product_summary["ProductName"] == product_name].iloc[0]

def get_product_df(product_name):
    return df[df["ProductName"] == product_name]

def build_gauge(health_score, title="Health Score"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_score,
        title={"text": title},
        gauge={
            "axis": {"range": [-100, 100]},
            "bar":  {"color": "white"},
            "steps": [
                {"range": [-100, -20], "color": "#7f1d1d"},
                {"range": [-20,   20], "color": "#78350f"},
                {"range": [20,   100], "color": "#14532d"}
            ]
        }
    ))
    fig.update_layout(template="plotly_dark", height=280, margin=dict(t=40, b=10))
    return fig

def build_sentiment_pie(product_name):
    row = get_summary_row(product_name)
    pos = row["Number of Positive Reviews"]
    neg = row["Number of Negative Reviews"]
    neu = row["Total Reviews"] - pos - neg
    fig = go.Figure(go.Pie(
        labels=["Positive", "Neutral", "Negative"],
        values=[pos, max(neu, 0), neg],
        hole=0.5,
        marker_colors=["#22c55e", "#64748b", "#ef4444"],
        textinfo="percent+label",
        showlegend=False
    ))
    fig.update_layout(
        template="plotly_dark",
        height=280,
        margin=dict(t=20, b=10, l=10, r=10),
        title=dict(text=product_name, x=0.5, font=dict(size=13))
    )
    return fig

def build_issue_bar(product_name):
    prod_df = get_product_df(product_name)
    counts = (
        prod_df["DetectedIssue"]
        .value_counts()
        .reset_index()
    )
    counts.columns = ["Issue", "Count"]
    counts = counts[counts["Issue"] != "No Issue Detected"]
    if counts.empty:
        return None
    fig = px.bar(
        counts,
        x="Count",
        y="Issue",
        orientation="h",
        color="Count",
        color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
        template="plotly_dark"
    )
    fig.update_layout(
        height=280,
        margin=dict(t=20, b=10, l=10, r=10),
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed")
    )
    return fig

def build_sentiment_distribution(product_name):
    prod_df = get_product_df(product_name)
    if "SentimentScore" not in prod_df.columns:
        return None
    fig = px.histogram(
        prod_df,
        x="SentimentScore",
        nbins=20,
        color_discrete_sequence=["#3b82f6"],
        template="plotly_dark",
        labels={"SentimentScore": "Sentiment Score", "count": "Reviews"}
    )
    fig.update_layout(
        height=280,
        margin=dict(t=20, b=10),
        bargap=0.05
    )
    return fig

# ==========================================================
# GROWTH PLAYBOOK + RECOMMENDATIONS (unchanged logic)
# ==========================================================

GROWTH_PLAYBOOK = {
    "Climbing Rope":    ["**Summit Socials:** Launch milestone tagging campaigns.", "**Adventure Bundling:** Partner with climbing gyms.", "**Safety Authority:** Host safety education streams."],
    "Basketball":       ["**Streetball Sponsorship:** Sponsor 3v3 tournaments.", "**Bulk Pricing for Coaches:** Introduce school pricing tiers.", "**Viral Campaign:** Launch trick-shot challenges."],
    "Ski Boots":        ["**Free Fit Trials:** Partner with ski resorts.", "**Athlete Sponsorship:** Promote durability.", "**Early Bird Discount:** Seasonal pre-orders."],
    "Ice Skates":       ["**Rink Partnerships:** Official skate branding.", "**Performance Clinics:** Host skating sessions.", "**Upgrade Program:** Beginner-to-Pro transition."],
    "Kayak":            ["**Eco Campaigns:** River cleanups.", "**Demo Popups:** Weekend lake trials.", "**Accessory Bundles:** Roof rack combo offers."],
    "Football Helmet":  ["**Safety Campaign:** Youth fitting seminars.", "**Bulk Customization:** Logo decals.", "**Tech Marketing:** Highlight impact absorption."],
    "Swim Goggles":     ["**No-Fog Guarantee:** 90-day promise.", "**Swim School Partnerships:** Starter kits.", "**Bundle Strategy:** Cap + shampoo combo."],
    "Cycling Helmet":   ["**Commuter Targeting:** Urban safety ads.", "**Retail Partnerships:** QR code kiosks.", "**Limited Edition Line:** High visibility colors."],
    "Fitness Tracker":  ["**Corporate Health Programs:** HR deals.", "**Influencer Reviews:** Endurance testing.", "**App Leaderboard Rewards:** Accessory discounts."],
    "Tennis Racket":    ["**Demo Events:** Local club trials.", "**Free Stringing Service:** Add value.", "**Youth Camp Sponsorship:** Brand visibility."],
    "Running Shoes":    ["**Run Club Sponsorship:** Community engagement.", "**Marathon Booths:** Trial experiences.", "**Mileage Rewards:** Repeat purchase triggers."],
    "Golf Clubs":       ["**Driving Range Demos:** Test experiences.", "**Coaching Bundles:** Include lessons.", "**Virtual Fitting:** Online consultation."],
    "Yoga Mat":         ["**Studio Affiliate Program:** Commission model.", "**Eco Branding:** Sustainability focus.", "**Outdoor Events:** Free community sessions."],
    "Dumbbells":        ["**Workout Guides:** QR unlock content.", "**Upgrade Discount:** Weight progression.", "**Apartment Targeting:** Compact design marketing."],
    "Baseball Glove":   ["**Premium Break-In Service:** Value add.", "**Youth League Sponsorship:** Opening day visibility.", "**Custom Stitching:** Personalization offer."],
    "Volleyball":       ["**Beach Tournament Branding:** Official ball status.", "**Club Bulk Pricing:** Team deals.", "**Skill Tutorials:** YouTube SEO strategy."],
    "Surfboard":        ["**Surf School Leasing:** Brand visibility.", "**Designer Storytelling:** Technical differentiation.", "**Eco Bundle:** Organic wax inclusion."],
    "Soccer Ball":      ["**Freestyle Contest:** Instagram engagement.", "**Futsal Version:** Low bounce edition.", "**Performance Ads:** High-speed flight shots."],
    "Boxing Gloves":    ["**Starter Kits:** Bundle hand wraps.", "**Gym Partnerships:** Replace house gloves.", "**Durability Videos:** Stress tests."],
    "Hockey Stick":     ["**Trial Nights:** Public skate demos.", "**Grip Tape Add-On:** Upsell accessory.", "**Flex Calculator Tool:** Personalization."]
}

RECOMMENDATIONS = {
    "Delivery Issue":     ["**Ship Faster:** Dispatch within 12 hours.", "**Courier Optimization:** Improve carrier selection.", "**Real-Time Tracking:** SMS notifications.", "**Compensation Policy:** Automatic discount for delays."],
    "Product Quality":    ["**Batch Audit:** Inspect recent production.", "**Factory Escalation:** Feedback loop to manufacturer.", "**Extended Warranty:** 6-month guarantee.", "**Material Upgrade:** Improve durability."],
    "Pricing Issue":      ["**Bundle Offers:** Add high-margin accessories.", "**Competitive Review:** Weekly pricing check.", "**Installment Plans:** Reduce upfront barrier.", "**Value Communication:** Highlight premium features."],
    "Customer Service":   ["**4-Hour SLA:** Faster response time.", "**Chatbot Automation:** FAQ handling.", "**Executive Escalation:** Manager outreach.", "**Follow-Up Email:** Post-purchase care."],
    "Packaging Issue":    ["**Reinforced Packaging:** Reduce damages.", "**Premium Unboxing:** Improve experience.", "**Eco Materials:** Sustainable + sturdy.", "**Easy-Open Design:** Frustration-free."],
    "Performance Issue":  ["**Instructional Videos:** Prevent misuse.", "**Internal Testing:** Stress validation.", "**Firmware Update:** Fix known issues.", "**Expert Guides:** Weekly best practices."],
    "Usability Issue":    ["**Simplified Manual:** 3-step clarity.", "**QR Video Guide:** Easy access support.", "**Quick Start Card:** Immediate clarity.", "**Community Forum:** Peer assistance."],
    "Expectation Gap":    ["**Real Photos:** Authentic visuals.", "**Clear Size Guide:** Context images.", "**Honest Positioning:** Set correct expectations.", "**Comparison Table:** Model differences."]
}

# ==========================================================
# PAGE 1 — PRODUCT RANKINGS
# ==========================================================

if page == "🏆 Product Rankings":
    st.title("🏆 Product Health Ranking")

    # Top-level fleet KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Products",   len(filtered_summary))
    k2.metric("Avg Health Score", f"{filtered_summary['Overall Health Score'].mean():.1f}")
    k3.metric("At Risk",          len(filtered_summary[filtered_summary["Overall Health Score"] < -20]))
    k4.metric("Strong Performers",len(filtered_summary[filtered_summary["Overall Health Score"] > 20]))

    st.markdown("---")

    # Health score bar chart — all products
    fig_bar = px.bar(
        filtered_summary.sort_values("Overall Health Score"),
        x="Overall Health Score",
        y="ProductName",
        orientation="h",
        color="Overall Health Score",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        range_color=[-100, 100],
        template="plotly_dark",
        labels={"ProductName": ""}
    )
    fig_bar.update_layout(
        height=max(350, len(filtered_summary) * 28),
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=30, b=10)
    )
    st.subheader("Health Score by Product")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("Full Rankings Table")
    st.dataframe(filtered_summary, use_container_width=True)

# ==========================================================
# PAGE 2 — DEEP DIVE
# ==========================================================

elif page == "🔍 Deep Dive":
    st.title("🔍 Product Deep Dive")

    selected_product = st.selectbox("Select Product", all_products)

    row       = get_summary_row(selected_product)
    prod_df   = get_product_df(selected_product)

    total_reviews   = row["Total Reviews"]
    positive_reviews= row["Number of Positive Reviews"]
    negative_reviews= row["Number of Negative Reviews"]
    positive_pct    = row["Positive Review Percentage (%)"]
    negative_pct    = row["Negative Review Percentage (%)"]
    health_score    = row["Overall Health Score"]

    # KPIs
    st.subheader("📌 Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Reviews",    int(total_reviews))
    c2.metric("Positive Reviews", int(positive_reviews), delta=f"{positive_pct:.1f}%")
    c3.metric("Negative Reviews", int(negative_reviews), delta=f"-{negative_pct:.1f}%", delta_color="inverse")
    c4.metric("Health Score",     f"{health_score:.1f}")

    # Alert
    alert = get_alert_badge(negative_pct)
    if negative_pct > 40:
        st.error(f"🚨 Critical Risk: High negative sentiment detected — {negative_pct:.1f}% negative reviews")
    elif negative_pct > 25:
        st.warning(f"⚠️ Moderate Risk: Rising negative sentiment — {negative_pct:.1f}% negative reviews")
    else:
        st.success(f"✅ Product health stable — {negative_pct:.1f}% negative reviews")

    st.markdown("---")

    # 3-column chart layout
    ch1, ch2, ch3 = st.columns(3)

    with ch1:
        st.markdown("**Sentiment Breakdown**")
        st.plotly_chart(build_sentiment_pie(selected_product), use_container_width=True)

    with ch2:
        st.markdown("**Health Score Gauge**")
        st.plotly_chart(build_gauge(health_score), use_container_width=True)

    with ch3:
        st.markdown("**Complaint Distribution**")
        fig_issue = build_issue_bar(selected_product)
        if fig_issue:
            st.plotly_chart(fig_issue, use_container_width=True)
        else:
            st.success("No major complaints detected.")

    # Sentiment score distribution
    fig_hist = build_sentiment_distribution(selected_product)
    if fig_hist:
        st.markdown("**Sentiment Score Distribution**")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # Issue recommendations
    issue_counts = prod_df["DetectedIssue"].value_counts().reset_index()
    issue_counts.columns = ["Issue Category", "Number of Reviews"]
    actual_issues = issue_counts[issue_counts["Issue Category"] != "No Issue Detected"]
    top_two_issues = actual_issues.head(2)["Issue Category"].tolist()
    top_issue = top_two_issues[0] if top_two_issues else None

    if top_two_issues:
        st.subheader("🚩 Action Plan")
        for issue in top_two_issues:
            if issue in RECOMMENDATIONS:
                with st.expander(f"Immediate Steps for: {issue}", expanded=True):
                    for r in RECOMMENDATIONS[issue]:
                        st.write(f"• {r}")
    else:
        st.success("✅ Top performer — no major issues detected.")

    st.markdown("---")

    # Growth playbook
    if st.button("🚀 Reveal Growth Strategies"):
        st.subheader(f"Growth Playbook — {selected_product}")
        strategies = GROWTH_PLAYBOOK.get(selected_product, [
            "**UGC Ads:** Turn 5-star reviews into video ads.",
            "**Loyalty Rewards:** Early access perks.",
            "**Referral Program:** Give 15%, Get 15%."
        ])
        for s in strategies:
            st.write(f"📈 {s}")

    st.markdown("---")

    # Top reviews
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("🔥 Top 5 Positive Reviews")
        st.dataframe(
            prod_df.sort_values("SentimentScore", ascending=False)
            .head(5)[["ReviewText", "SentimentScore"]],
            use_container_width=True
        )
    with r2:
        st.subheader("⚠️ Top 5 Negative Reviews")
        st.dataframe(
            prod_df.sort_values("SentimentScore")
            .head(5)[["ReviewText", "SentimentScore"]],
            use_container_width=True
        )

# ==========================================================
# PAGE 3 — COMPARE PRODUCTS
# ==========================================================

elif page == "⚔️ Compare Products":
    st.title("⚔️ Side-by-Side Product Comparison")

    col_a, col_b = st.columns(2)
    with col_a:
        product_a = st.selectbox("Product A", all_products, index=0, key="pa")
    with col_b:
        product_b = st.selectbox("Product B", all_products, index=min(1, len(all_products)-1), key="pb")

    if product_a == product_b:
        st.warning("Select two different products to compare.")
        st.stop()

    row_a = get_summary_row(product_a)
    row_b = get_summary_row(product_b)

    st.markdown("---")

    # KPI comparison
    st.subheader("📊 Key Metrics Comparison")
    metrics = ["Total Reviews", "Overall Health Score",
               "Positive Review Percentage (%)", "Negative Review Percentage (%)",
               "Average Sentiment Score"]

    m_cols = st.columns(len(metrics))
    for col, metric in zip(m_cols, metrics):
        val_a = row_a[metric]
        val_b = row_b[metric]
        winner = product_a if val_a > val_b else product_b
        fmt = ".1f" if isinstance(val_a, float) else "d"
        col.metric(
            label=metric.replace(" (%)", ""),
            value=f"{val_a:{fmt}}",
            delta=f"{val_a - val_b:+.1f} vs {product_b}"
        )

    st.markdown("---")

    # Side-by-side charts
    left, right = st.columns(2)

    with left:
        st.markdown(f"#### {product_a}")
        st.plotly_chart(build_sentiment_pie(product_a),  use_container_width=True)
        st.plotly_chart(build_gauge(row_a["Overall Health Score"], product_a), use_container_width=True)
        fig_issue_a = build_issue_bar(product_a)
        if fig_issue_a:
            st.plotly_chart(fig_issue_a, use_container_width=True)
        else:
            st.success("No major complaints.")

    with right:
        st.markdown(f"#### {product_b}")
        st.plotly_chart(build_sentiment_pie(product_b),  use_container_width=True)
        st.plotly_chart(build_gauge(row_b["Overall Health Score"], product_b), use_container_width=True)
        fig_issue_b = build_issue_bar(product_b)
        if fig_issue_b:
            st.plotly_chart(fig_issue_b, use_container_width=True)
        else:
            st.success("No major complaints.")

    st.markdown("---")

    # Radar chart comparison
    st.subheader("🕸️ Multi-Metric Radar")
    radar_metrics = {
        "Health Score (norm)": ("Overall Health Score", -100, 100),
        "Positive %":          ("Positive Review Percentage (%)", 0, 100),
        "Avg Sentiment":       ("Average Sentiment Score", -1, 1),
        "Review Volume":       ("Total Reviews", 0, product_summary["Total Reviews"].max()),
    }

    def normalise(val, lo, hi):
        return max(0, min(100, (val - lo) / (hi - lo) * 100))

    labels = list(radar_metrics.keys())
    vals_a = [normalise(row_a[v], lo, hi) for _, (v, lo, hi) in radar_metrics.items()]
    vals_b = [normalise(row_b[v], lo, hi) for _, (v, lo, hi) in radar_metrics.items()]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=vals_a + [vals_a[0]], theta=labels + [labels[0]],
                                        fill="toself", name=product_a, line_color="#22c55e"))
    fig_radar.add_trace(go.Scatterpolar(r=vals_b + [vals_b[0]], theta=labels + [labels[0]],
                                        fill="toself", name=product_b, line_color="#3b82f6", opacity=0.7))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template="plotly_dark",
        height=420
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # Verdict
    st.subheader("🏁 Verdict")
    score_a = row_a["Overall Health Score"]
    score_b = row_b["Overall Health Score"]
    if score_a > score_b:
        st.success(f"**{product_a}** leads with a health score of {score_a:.1f} vs {score_b:.1f}")
    elif score_b > score_a:
        st.success(f"**{product_b}** leads with a health score of {score_b:.1f} vs {score_a:.1f}")
    else:
        st.info("Both products are evenly matched on health score.")

# ==========================================================
# PAGE 4 — AI EXECUTIVE REPORT
# ==========================================================

elif page == "🤖 AI Executive Report":
    st.title("🤖 AI Executive Report")
    st.markdown("Powered by Groq (Llama 3) — generates a real narrative summary from the data, not a template.")

    selected_product = st.selectbox("Select Product", all_products, key="ai_product")

    row        = get_summary_row(selected_product)
    prod_df    = get_product_df(selected_product)

    total_reviews    = int(row["Total Reviews"])
    positive_reviews = int(row["Number of Positive Reviews"])
    negative_reviews = int(row["Number of Negative Reviews"])
    positive_pct     = row["Positive Review Percentage (%)"]
    negative_pct     = row["Negative Review Percentage (%)"]
    health_score     = row["Overall Health Score"]

    issue_counts = prod_df["DetectedIssue"].value_counts().reset_index()
    issue_counts.columns = ["Issue", "Count"]
    issues_str = issue_counts[issue_counts["Issue"] != "No Issue Detected"].to_string(index=False)

    top_pos_reviews = (
        prod_df.sort_values("SentimentScore", ascending=False)
        .head(3)["ReviewText"].tolist()
    )
    top_neg_reviews = (
        prod_df.sort_values("SentimentScore")
        .head(3)["ReviewText"].tolist()
    )

    # Build prompt
    prompt = f"""You are a senior marketing analytics consultant writing an executive intelligence briefing.

Product: {selected_product}
Total Reviews: {total_reviews}
Positive Reviews: {positive_reviews} ({positive_pct:.1f}%)
Negative Reviews: {negative_reviews} ({negative_pct:.1f}%)
Health Score: {health_score:.1f} (range -100 to 100)

Complaint breakdown:
{issues_str if issues_str.strip() else "No significant issues detected"}

Sample positive reviews:
{chr(10).join(f'- {r}' for r in top_pos_reviews)}

Sample negative reviews:
{chr(10).join(f'- {r}' for r in top_neg_reviews)}

Write a concise executive briefing (4-6 paragraphs) that:
1. Opens with a sharp assessment of overall product health
2. Calls out the key strengths from customer feedback
3. Identifies the most critical risk areas with specific evidence from reviews
4. Gives 3 concrete, prioritised action items for the product team
5. Closes with a forward outlook

Write like a sharp business consultant — confident, specific, no fluff. No bullet lists, flowing paragraphs only."""

    if st.button("✨ Generate AI Executive Summary"):
        with st.spinner("Analysing product data and writing summary..."):
            try:
                client = Groq()
                ai_text = ""
                summary_placeholder = st.empty()

                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )

                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        ai_text += delta
                        summary_placeholder.markdown(
                            f"""<div style="background:#161B22; border:1px solid #30363D;
                            border-radius:10px; padding:20px; line-height:1.8;">
                            {ai_text}
                            </div>""",
                            unsafe_allow_html=True
                        )

                st.session_state["ai_summary"]      = ai_text
                st.session_state["ai_product_name"] = selected_product

            except Exception as e:
                st.error(f"AI generation failed: {e}")

    # PDF download (uses cached summary if available)
    if st.session_state.get("ai_summary") and st.session_state.get("ai_product_name") == selected_product:
        ai_text = st.session_state["ai_summary"]

        st.markdown("---")
        st.subheader("📄 Download Report")

        if st.button("Build PDF Report"):
            buffer = io.BytesIO()
            doc    = SimpleDocTemplate(buffer, rightMargin=inch, leftMargin=inch,
                                       topMargin=inch, bottomMargin=inch)
            styles = getSampleStyleSheet()
            body_style = ParagraphStyle(
                "body", parent=styles["Normal"],
                fontSize=11, leading=16, spaceAfter=12
            )
            elements = [
                Paragraph(f"Product Intelligence Executive Report", styles["Heading1"]),
                Paragraph(f"Product: {selected_product}", styles["Heading2"]),
                Spacer(1, 0.3 * inch),
                Paragraph("Key Metrics", styles["Heading3"]),
            ]

            data = [
                ["Metric", "Value"],
                ["Total Reviews",      str(total_reviews)],
                ["Positive Reviews",   f"{positive_reviews} ({positive_pct:.1f}%)"],
                ["Negative Reviews",   f"{negative_reviews} ({negative_pct:.1f}%)"],
                ["Overall Health Score", f"{health_score:.1f}"],
            ]
            tbl = Table(data, colWidths=[3 * inch, 3 * inch])
            tbl.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), rl_colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), rl_colors.white),
                ("GRID",        (0, 0), (-1, -1), 0.5, rl_colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.HexColor("#f8fafc"), rl_colors.white]),
                ("FONTSIZE",    (0, 0), (-1, -1), 10),
                ("PADDING",     (0, 0), (-1, -1), 8),
            ]))
            elements += [tbl, Spacer(1, 0.3 * inch),
                         Paragraph("AI Executive Summary", styles["Heading3"]),
                         Paragraph(ai_text.replace("\n", "<br/>"), body_style)]

            doc.build(elements)

            st.download_button(
                label="📥 Download PDF",
                data=buffer.getvalue(),
                file_name=f"{selected_product}_Intelligence_Report.pdf",
                mime="application/pdf"
            )
