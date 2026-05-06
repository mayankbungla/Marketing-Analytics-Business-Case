# ==========================================================
# PRODUCT REVIEW INTELLIGENCE DASHBOARD
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

# ==========================================================
# DARK / LIGHT MODE TOGGLE
# ==========================================================

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

dark = st.session_state["dark_mode"]

if dark:
    BG        = "#0E1117"
    CARD_BG   = "#161B22"
    BORDER    = "#30363D"
    TEXT      = "#E6EDF3"
    PLOT_TPL  = "plotly_dark"
    INPUT_BG  = "#161B22"
else:
    BG        = "#F6F8FA"
    CARD_BG   = "#FFFFFF"
    BORDER    = "#D0D7DE"
    TEXT      = "#1F2328"
    PLOT_TPL  = "plotly_white"
    INPUT_BG  = "#FFFFFF"

st.markdown(f"""
<style>
.stApp {{ background-color: {BG}; color: {TEXT}; }}
body, p, span, div, label {{ color: {TEXT} !important; }}
section[data-testid="stSidebar"] {{
    background-color: {CARD_BG};
    border-right: 1px solid {BORDER};
}}
div[data-testid="metric-container"] {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 16px;
}}
h1, h2, h3 {{ color: {TEXT} !important; }}
h2 {{ border-bottom: 1px solid {BORDER}; padding-bottom: 6px; }}
.stTextInput > div > div > input {{
    background-color: {INPUT_BG};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
.stDataFrame {{ border: 1px solid {BORDER}; border-radius: 8px; }}
details {{ background: {CARD_BG}; border: 1px solid {BORDER}; border-radius:8px; padding:8px; }}
.nl-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 20px;
    line-height: 1.8;
    color: {TEXT};
    margin-top: 12px;
}}
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
    df_reviews = pd.read_csv(review_files[-1])
    df_summary = pd.read_csv(summary_files[-1])
    return df_reviews, df_summary

df, product_summary = load_data()

if df is None or product_summary is None:
    st.error("Processed intelligence files not found. Run review_intelligence_engine.py first.")
    st.stop()

product_summary = product_summary.rename(columns={
    "TotalReviews":    "Total Reviews",
    "AvgSentiment":    "Average Sentiment Score",
    "NegativeReviews": "Number of Negative Reviews",
    "PositiveReviews": "Number of Positive Reviews",
    "NegativePct":     "Negative Review Percentage (%)",
    "PositivePct":     "Positive Review Percentage (%)",
    "HealthScore":     "Overall Health Score"
})

product_summary = product_summary.sort_values("Overall Health Score", ascending=False)
all_products    = sorted(product_summary["ProductName"].unique())

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown("## 📊 Intelligence Hub")

    mode_label = "☀️ Light Mode" if dark else "🌙 Dark Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state["dark_mode"] = not dark
        st.rerun()

    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "🏆 Product Rankings",
            "🔍 Deep Dive",
            "⚔️ Compare Products",
            "📊 Data & Analysis",
            "🤖 AI Executive Report",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🎛️ Global Filters")

    search_query = st.text_input("🔍 Search product", placeholder="e.g. Hockey...")

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
    st.caption("ShopEasy · Product Intelligence")

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

# Search-filtered product list for dropdowns
if search_query:
    search_products = [p for p in all_products if search_query.lower() in p.lower()]
else:
    search_products = all_products

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_summary_row(product_name):
    return product_summary[product_summary["ProductName"] == product_name].iloc[0]

def get_product_df(product_name):
    return df[df["ProductName"] == product_name]

def build_gauge(health_score, title="Health Score"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_score,
        title={"text": title, "font": {"size": 14}},
        number={"font": {"size": 36}},
        gauge={
            "axis": {"range": [-100, 100], "tickwidth": 1},
            "bar":  {"color": "#60a5fa", "thickness": 0.25},
            "steps": [
                {"range": [-100, -20], "color": "#7f1d1d"},
                {"range": [-20,   20], "color": "#78350f"},
                {"range": [20,   100], "color": "#14532d"}
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": health_score
            }
        }
    ))
    fig.update_layout(
        template=PLOT_TPL,
        height=260,
        margin=dict(t=50, b=10, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def build_sentiment_pie(product_name):
    row = get_summary_row(product_name)
    pos = row["Number of Positive Reviews"]
    neg = row["Number of Negative Reviews"]
    neu = max(row["Total Reviews"] - pos - neg, 0)
    fig = go.Figure(go.Pie(
        labels=["Positive", "Neutral", "Negative"],
        values=[pos, neu, neg],
        hole=0.55,
        marker_colors=["#22c55e", "#64748b", "#ef4444"],
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value} reviews (%{percent})<extra></extra>",
        showlegend=True
    ))
    fig.update_layout(
        template=PLOT_TPL,
        height=300,
        margin=dict(t=10, b=30, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def build_issue_bar(product_name):
    prod_df = get_product_df(product_name)
    counts  = prod_df["DetectedIssue"].value_counts().reset_index()
    counts.columns = ["Issue", "Count"]
    counts  = counts[counts["Issue"] != "No Issue Detected"]
    if counts.empty:
        return None
    fig = px.bar(
        counts,
        x="Count",
        y="Issue",
        orientation="h",
        color="Count",
        color_continuous_scale=["#22c55e", "#f59e0b", "#ef4444"],
        template=PLOT_TPL,
        text="Count"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=max(220, len(counts) * 48 + 60),
        margin=dict(t=10, b=10, l=10, r=70),
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
        xaxis=dict(title=""),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def build_sentiment_histogram(product_name):
    prod_df = get_product_df(product_name)
    if "SentimentScore" not in prod_df.columns:
        return None
    fig = px.histogram(
        prod_df,
        x="SentimentScore",
        nbins=20,
        color_discrete_sequence=["#3b82f6"],
        template=PLOT_TPL,
        labels={"SentimentScore": "Sentiment Score"}
    )
    fig.update_layout(
        height=280,
        margin=dict(t=10, b=10),
        bargap=0.05,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# ==========================================================
# PLAYBOOK & RECOMMENDATIONS
# ==========================================================

GROWTH_PLAYBOOK = {
    "Climbing Rope":   ["**Summit Socials:** Launch milestone tagging campaigns.", "**Adventure Bundling:** Partner with climbing gyms.", "**Safety Authority:** Host safety education streams."],
    "Basketball":      ["**Streetball Sponsorship:** Sponsor 3v3 tournaments.", "**Bulk Pricing for Coaches:** Introduce school pricing tiers.", "**Viral Campaign:** Launch trick-shot challenges."],
    "Ski Boots":       ["**Free Fit Trials:** Partner with ski resorts.", "**Athlete Sponsorship:** Promote durability.", "**Early Bird Discount:** Seasonal pre-orders."],
    "Ice Skates":      ["**Rink Partnerships:** Official skate branding.", "**Performance Clinics:** Host skating sessions.", "**Upgrade Program:** Beginner-to-Pro transition."],
    "Kayak":           ["**Eco Campaigns:** River cleanups.", "**Demo Popups:** Weekend lake trials.", "**Accessory Bundles:** Roof rack combo offers."],
    "Football Helmet": ["**Safety Campaign:** Youth fitting seminars.", "**Bulk Customization:** Logo decals.", "**Tech Marketing:** Highlight impact absorption."],
    "Swim Goggles":    ["**No-Fog Guarantee:** 90-day promise.", "**Swim School Partnerships:** Starter kits.", "**Bundle Strategy:** Cap + shampoo combo."],
    "Cycling Helmet":  ["**Commuter Targeting:** Urban safety ads.", "**Retail Partnerships:** QR code kiosks.", "**Limited Edition Line:** High visibility colors."],
    "Fitness Tracker": ["**Corporate Health Programs:** HR deals.", "**Influencer Reviews:** Endurance testing.", "**App Leaderboard Rewards:** Accessory discounts."],
    "Tennis Racket":   ["**Demo Events:** Local club trials.", "**Free Stringing Service:** Add value.", "**Youth Camp Sponsorship:** Brand visibility."],
    "Running Shoes":   ["**Run Club Sponsorship:** Community engagement.", "**Marathon Booths:** Trial experiences.", "**Mileage Rewards:** Repeat purchase triggers."],
    "Golf Clubs":      ["**Driving Range Demos:** Test experiences.", "**Coaching Bundles:** Include lessons.", "**Virtual Fitting:** Online consultation."],
    "Yoga Mat":        ["**Studio Affiliate Program:** Commission model.", "**Eco Branding:** Sustainability focus.", "**Outdoor Events:** Free community sessions."],
    "Dumbbells":       ["**Workout Guides:** QR unlock content.", "**Upgrade Discount:** Weight progression.", "**Apartment Targeting:** Compact design marketing."],
    "Baseball Glove":  ["**Premium Break-In Service:** Value add.", "**Youth League Sponsorship:** Opening day visibility.", "**Custom Stitching:** Personalization offer."],
    "Volleyball":      ["**Beach Tournament Branding:** Official ball status.", "**Club Bulk Pricing:** Team deals.", "**Skill Tutorials:** YouTube SEO strategy."],
    "Surfboard":       ["**Surf School Leasing:** Brand visibility.", "**Designer Storytelling:** Technical differentiation.", "**Eco Bundle:** Organic wax inclusion."],
    "Soccer Ball":     ["**Freestyle Contest:** Instagram engagement.", "**Futsal Version:** Low bounce edition.", "**Performance Ads:** High-speed flight shots."],
    "Boxing Gloves":   ["**Starter Kits:** Bundle hand wraps.", "**Gym Partnerships:** Replace house gloves.", "**Durability Videos:** Stress tests."],
    "Hockey Stick":    ["**Trial Nights:** Public skate demos.", "**Grip Tape Add-On:** Upsell accessory.", "**Flex Calculator Tool:** Personalization."]
}

RECOMMENDATIONS = {
    "Delivery Issue":    ["**Ship Faster:** Dispatch within 12 hours.", "**Courier Optimization:** Improve carrier selection.", "**Real-Time Tracking:** SMS notifications.", "**Compensation Policy:** Automatic discount for delays."],
    "Product Quality":   ["**Batch Audit:** Inspect recent production.", "**Factory Escalation:** Feedback loop to manufacturer.", "**Extended Warranty:** 6-month guarantee.", "**Material Upgrade:** Improve durability."],
    "Pricing Issue":     ["**Bundle Offers:** Add high-margin accessories.", "**Competitive Review:** Weekly pricing check.", "**Installment Plans:** Reduce upfront barrier.", "**Value Communication:** Highlight premium features."],
    "Customer Service":  ["**4-Hour SLA:** Faster response time.", "**Chatbot Automation:** FAQ handling.", "**Executive Escalation:** Manager outreach.", "**Follow-Up Email:** Post-purchase care."],
    "Packaging Issue":   ["**Reinforced Packaging:** Reduce damages.", "**Premium Unboxing:** Improve experience.", "**Eco Materials:** Sustainable + sturdy.", "**Easy-Open Design:** Frustration-free."],
    "Performance Issue": ["**Instructional Videos:** Prevent misuse.", "**Internal Testing:** Stress validation.", "**Firmware Update:** Fix known issues.", "**Expert Guides:** Weekly best practices."],
    "Usability Issue":   ["**Simplified Manual:** 3-step clarity.", "**QR Video Guide:** Easy access support.", "**Quick Start Card:** Immediate clarity.", "**Community Forum:** Peer assistance."],
    "Expectation Gap":   ["**Real Photos:** Authentic visuals.", "**Clear Size Guide:** Context images.", "**Honest Positioning:** Set correct expectations.", "**Comparison Table:** Model differences."]
}

# ==========================================================
# PAGE 1 — PRODUCT RANKINGS
# ==========================================================

if page == "🏆 Product Rankings":
    st.title("🏆 Product Health Ranking")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Products",    len(filtered_summary))
    k2.metric("Avg Health Score",  f"{filtered_summary['Overall Health Score'].mean():.1f}")
    k3.metric("At Risk",           len(filtered_summary[filtered_summary["Overall Health Score"] < -20]))
    k4.metric("Strong Performers", len(filtered_summary[filtered_summary["Overall Health Score"] > 20]))

    st.markdown("---")

    fig_bar = px.bar(
        filtered_summary.sort_values("Overall Health Score"),
        x="Overall Health Score",
        y="ProductName",
        orientation="h",
        color="Overall Health Score",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        range_color=[-100, 100],
        template=PLOT_TPL,
        labels={"ProductName": "", "Overall Health Score": "Health Score"},
        text="Overall Health Score"
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_bar.update_layout(
        height=max(420, len(filtered_summary) * 38),
        coloraxis_showscale=False,
        margin=dict(l=10, r=80, t=30, b=10),
        yaxis=dict(tickfont=dict(size=13)),
        paper_bgcolor="rgba(0,0,0,0)"
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

    selected_product = st.selectbox(
        "Select Product",
        search_products if search_products else all_products,
        help="Use the search bar in the sidebar to filter this list"
    )
    if search_query:
        st.caption(f"Showing {len(search_products)} product(s) matching '{search_query}'")

    row     = get_summary_row(selected_product)
    prod_df = get_product_df(selected_product)

    total_reviews    = row["Total Reviews"]
    positive_reviews = row["Number of Positive Reviews"]
    negative_reviews = row["Number of Negative Reviews"]
    positive_pct     = row["Positive Review Percentage (%)"]
    negative_pct     = row["Negative Review Percentage (%)"]
    health_score     = row["Overall Health Score"]

    st.subheader("📌 Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Reviews",    int(total_reviews))
    c2.metric("Positive Reviews", int(positive_reviews), delta=f"{positive_pct:.1f}%")
    c3.metric("Negative Reviews", int(negative_reviews), delta=f"-{negative_pct:.1f}%", delta_color="inverse")
    c4.metric("Health Score",     f"{health_score:.1f}")

    if negative_pct > 40:
        st.error(f"🚨 Critical Risk: {negative_pct:.1f}% negative reviews")
    elif negative_pct > 25:
        st.warning(f"⚠️ Moderate Risk: {negative_pct:.1f}% negative reviews")
    else:
        st.success(f"✅ Stable: {negative_pct:.1f}% negative reviews")

    st.markdown("---")

    # Row 1: Pie | Gauge — 2 columns, no 3-way cramping
    col_pie, col_gauge = st.columns(2)
    with col_pie:
        st.markdown("#### 🍩 Sentiment Breakdown")
        st.plotly_chart(build_sentiment_pie(selected_product), use_container_width=True)
    with col_gauge:
        st.markdown("#### 🎯 Health Score Gauge")
        st.plotly_chart(build_gauge(health_score), use_container_width=True)

    st.markdown("---")

    # Row 2: Issue bar — full width so labels are never cut off
    st.markdown("#### 📋 Complaint Distribution")
    fig_issue = build_issue_bar(selected_product)
    if fig_issue:
        st.plotly_chart(fig_issue, use_container_width=True)
    else:
        st.success("No major complaints detected for this product.")

    # Row 3: Histogram — full width
    fig_hist = build_sentiment_histogram(selected_product)
    if fig_hist:
        st.markdown("#### 📈 Sentiment Score Distribution")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    issue_counts   = prod_df["DetectedIssue"].value_counts().reset_index()
    issue_counts.columns = ["Issue Category", "Number of Reviews"]
    actual_issues  = issue_counts[issue_counts["Issue Category"] != "No Issue Detected"]
    top_two_issues = actual_issues.head(2)["Issue Category"].tolist()
    top_issue      = top_two_issues[0] if top_two_issues else None

    if top_two_issues:
        st.subheader("🚩 Action Plan")
        for issue in top_two_issues:
            if issue in RECOMMENDATIONS:
                with st.expander(f"Steps for: {issue}", expanded=True):
                    for r in RECOMMENDATIONS[issue]:
                        st.write(f"• {r}")
    else:
        st.success("✅ Top performer — no major issues detected.")

    st.markdown("---")

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
        remaining = [p for p in all_products if p != product_a]
        product_b = st.selectbox("Product B", remaining, index=0, key="pb")

    row_a = get_summary_row(product_a)
    row_b = get_summary_row(product_b)

    st.markdown("---")

    st.subheader("📊 Key Metrics at a Glance")
    metrics = [
        ("Health Score",  "Overall Health Score"),
        ("Positive %",    "Positive Review Percentage (%)"),
        ("Negative %",    "Negative Review Percentage (%)"),
        ("Avg Sentiment", "Average Sentiment Score"),
        ("Total Reviews", "Total Reviews"),
    ]
    m_cols = st.columns(len(metrics))
    for col, (label, key) in zip(m_cols, metrics):
        val_a = row_a[key]
        val_b = row_b[key]
        col.metric(label=label, value=f"{val_a:.1f}", delta=f"{val_a - val_b:+.1f} vs {product_b}")

    st.markdown("---")

    # Each chart row labelled clearly — no overlap
    st.subheader("🍩 Sentiment Breakdown")
    left, right = st.columns(2)
    with left:
        st.markdown(f"**{product_a}**")
        st.plotly_chart(build_sentiment_pie(product_a), use_container_width=True)
    with right:
        st.markdown(f"**{product_b}**")
        st.plotly_chart(build_sentiment_pie(product_b), use_container_width=True)

    st.subheader("🎯 Health Score Gauges")
    left2, right2 = st.columns(2)
    with left2:
        st.markdown(f"**{product_a}**")
        st.plotly_chart(build_gauge(row_a["Overall Health Score"]), use_container_width=True)
    with right2:
        st.markdown(f"**{product_b}**")
        st.plotly_chart(build_gauge(row_b["Overall Health Score"]), use_container_width=True)

    st.subheader("📋 Complaint Breakdown")
    left3, right3 = st.columns(2)
    with left3:
        st.markdown(f"**{product_a}**")
        fig_a = build_issue_bar(product_a)
        st.plotly_chart(fig_a, use_container_width=True) if fig_a else st.success("No major issues.")
    with right3:
        st.markdown(f"**{product_b}**")
        fig_b = build_issue_bar(product_b)
        st.plotly_chart(fig_b, use_container_width=True) if fig_b else st.success("No major issues.")

    st.markdown("---")

    st.subheader("🕸️ Multi-Metric Radar")
    radar_metrics = {
        "Health Score":  ("Overall Health Score", -100, 100),
        "Positive %":    ("Positive Review Percentage (%)", 0, 100),
        "Avg Sentiment": ("Average Sentiment Score", -1, 1),
        "Review Volume": ("Total Reviews", 0, product_summary["Total Reviews"].max()),
    }

    def normalise(val, lo, hi):
        return max(0, min(100, (val - lo) / (hi - lo) * 100))

    labels = list(radar_metrics.keys())
    vals_a = [normalise(row_a[v], lo, hi) for _, (v, lo, hi) in radar_metrics.items()]
    vals_b = [normalise(row_b[v], lo, hi) for _, (v, lo, hi) in radar_metrics.items()]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_a + [vals_a[0]], theta=labels + [labels[0]],
        fill="toself", name=product_a, line_color="#22c55e"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_b + [vals_b[0]], theta=labels + [labels[0]],
        fill="toself", name=product_b, line_color="#3b82f6", opacity=0.7
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template=PLOT_TPL, height=420,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    st.subheader("🏁 Verdict")
    score_a = row_a["Overall Health Score"]
    score_b = row_b["Overall Health Score"]
    if score_a > score_b:
        st.success(f"**{product_a}** leads — Health Score {score_a:.1f} vs {score_b:.1f}")
    elif score_b > score_a:
        st.success(f"**{product_b}** leads — Health Score {score_b:.1f} vs {score_a:.1f}")
    else:
        st.info("Both products are evenly matched.")

# ==========================================================
# PAGE 4 — DATA & ANALYSIS
# ==========================================================

elif page == "📊 Data & Analysis":
    st.title("📊 Data & Analysis")
    st.markdown("Portfolio-wide analytics — scatter, heatmap, grouped bars, and a raw review explorer.")

    st.markdown("---")

    total_rev = int(product_summary["Total Reviews"].sum())
    avg_pos   = product_summary["Positive Review Percentage (%)"].mean()
    avg_neg   = product_summary["Negative Review Percentage (%)"].mean()
    avg_sent  = product_summary["Average Sentiment Score"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Reviews (All)",  f"{total_rev:,}")
    k2.metric("Avg Positive Rate",    f"{avg_pos:.1f}%")
    k3.metric("Avg Negative Rate",    f"{avg_neg:.1f}%")
    k4.metric("Avg Sentiment Score",  f"{avg_sent:.3f}")

    st.markdown("---")

    # Scatter: Volume vs Health Score
    st.subheader("📍 Review Volume vs Health Score")
    st.caption("Bubble size = negative review count. Reveals if popular products have hidden problems.")
    fig_scatter = px.scatter(
        product_summary,
        x="Total Reviews",
        y="Overall Health Score",
        size="Number of Negative Reviews",
        color="Overall Health Score",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        range_color=[-100, 100],
        hover_name="ProductName",
        template=PLOT_TPL,
        labels={"Overall Health Score": "Health Score"},
        size_max=40
    )
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
    fig_scatter.update_layout(
        height=420, coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # Issue heatmap
    st.subheader("🔥 Issue Heatmap — All Products")
    st.caption("How many reviews flagged each issue type per product.")
    issue_pivot = (
        df[df["DetectedIssue"] != "No Issue Detected"]
        .groupby(["ProductName", "DetectedIssue"])
        .size()
        .reset_index(name="Count")
        .pivot(index="ProductName", columns="DetectedIssue", values="Count")
        .fillna(0)
    )
    if not issue_pivot.empty:
        fig_heat = px.imshow(
            issue_pivot,
            color_continuous_scale=["#0E1117", "#f59e0b", "#ef4444"],
            template=PLOT_TPL,
            aspect="auto",
            labels=dict(color="Reviews")
        )
        fig_heat.update_layout(
            height=max(380, len(issue_pivot) * 34),
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(tickangle=-30, tickfont=dict(size=11)),
            yaxis=dict(tickfont=dict(size=11)),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # Grouped bar: Positive vs Negative %
    st.subheader("📊 Positive vs Negative Rate by Product")
    melted = product_summary[["ProductName", "Positive Review Percentage (%)", "Negative Review Percentage (%)"]].copy()
    melted = melted.melt(id_vars="ProductName", var_name="Type", value_name="Percentage")
    melted["Type"] = melted["Type"].str.replace(" Review Percentage (%)", "", regex=False)
    fig_grouped = px.bar(
        melted.sort_values("ProductName"),
        x="ProductName", y="Percentage", color="Type",
        barmode="group",
        color_discrete_map={"Positive": "#22c55e", "Negative": "#ef4444"},
        template=PLOT_TPL,
        labels={"Percentage": "%", "ProductName": ""}
    )
    fig_grouped.update_layout(
        height=420,
        xaxis=dict(tickangle=-35, tickfont=dict(size=11)),
        margin=dict(b=130, t=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_grouped, use_container_width=True)

    st.markdown("---")

    # Overall sentiment distribution
    st.subheader("📈 Overall Sentiment Score Distribution")
    if "SentimentScore" in df.columns:
        fig_all_hist = px.histogram(
            df, x="SentimentScore", nbins=30,
            color_discrete_sequence=["#3b82f6"],
            template=PLOT_TPL,
            labels={"SentimentScore": "Sentiment Score"}
        )
        fig_all_hist.update_layout(
            height=300, margin=dict(t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_all_hist, use_container_width=True)

    st.markdown("---")

    # Raw data explorer
    st.subheader("🗃️ Raw Review Data Explorer")
    explore_product = st.selectbox("Filter by product", ["All Products"] + all_products, key="explorer")
    explore_df = df if explore_product == "All Products" else df[df["ProductName"] == explore_product]

    col_kw, col_sent = st.columns(2)
    with col_kw:
        keyword = st.text_input("Search review text", placeholder="e.g. delivery, quality...")
    with col_sent:
        sent_filter = st.selectbox("Sentiment", ["All", "Positive", "Negative", "Neutral"], key="sent_filter")

    if keyword:
        explore_df = explore_df[explore_df["ReviewText"].str.contains(keyword, case=False, na=False)]
    if sent_filter != "All" and "SentimentCategory" in explore_df.columns:
        explore_df = explore_df[explore_df["SentimentCategory"] == sent_filter]

    st.caption(f"Showing {len(explore_df):,} reviews")
    cols_to_show = [c for c in ["ProductName", "ReviewText", "SentimentScore", "SentimentCategory", "DetectedIssue"] if c in explore_df.columns]
    st.dataframe(explore_df[cols_to_show].reset_index(drop=True), use_container_width=True, height=400)

# ==========================================================
# PAGE 5 — AI EXECUTIVE REPORT + NATURAL LANGUAGE SEARCH
# ==========================================================

elif page == "🤖 AI Executive Report":
    st.title("🤖 AI Executive Report")

    tab1, tab2 = st.tabs(["📄 Executive Summary", "💬 Natural Language Search"])

    # ── Tab 1: Executive Summary ──────────────────────────
    with tab1:
        st.markdown("Powered by Groq (Llama 3) — real AI narrative, not a template.")

        selected_product = st.selectbox(
            "Select Product",
            search_products if search_products else all_products,
            key="ai_product"
        )

        row     = get_summary_row(selected_product)
        prod_df = get_product_df(selected_product)

        total_reviews    = int(row["Total Reviews"])
        positive_reviews = int(row["Number of Positive Reviews"])
        negative_reviews = int(row["Number of Negative Reviews"])
        positive_pct     = row["Positive Review Percentage (%)"]
        negative_pct     = row["Negative Review Percentage (%)"]
        health_score     = row["Overall Health Score"]

        issue_counts = prod_df["DetectedIssue"].value_counts().reset_index()
        issue_counts.columns = ["Issue", "Count"]
        issues_str = issue_counts[issue_counts["Issue"] != "No Issue Detected"].to_string(index=False)

        top_pos = prod_df.sort_values("SentimentScore", ascending=False).head(3)["ReviewText"].tolist()
        top_neg = prod_df.sort_values("SentimentScore").head(3)["ReviewText"].tolist()

        prompt = f"""You are a senior marketing analytics consultant writing an executive intelligence briefing.

Product: {selected_product}
Total Reviews: {total_reviews}
Positive Reviews: {positive_reviews} ({positive_pct:.1f}%)
Negative Reviews: {negative_reviews} ({negative_pct:.1f}%)
Health Score: {health_score:.1f} (range -100 to 100)

Complaint breakdown:
{issues_str if issues_str.strip() else "No significant issues detected"}

Sample positive reviews:
{chr(10).join(f'- {r}' for r in top_pos)}

Sample negative reviews:
{chr(10).join(f'- {r}' for r in top_neg)}

Write a concise executive briefing (4-6 paragraphs):
1. Sharp overall health assessment
2. Key strengths from customer feedback
3. Critical risks with evidence from reviews
4. 3 concrete prioritised action items
5. Forward outlook

Style: confident, specific, no fluff, flowing paragraphs only."""

        if st.button("✨ Generate AI Executive Summary"):
            with st.spinner("Writing summary..."):
                try:
                    client  = Groq()
                    ai_text = ""
                    placeholder = st.empty()
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
                            placeholder.markdown(
                                f'<div class="nl-card">{ai_text}</div>',
                                unsafe_allow_html=True
                            )
                    st.session_state["ai_summary"]      = ai_text
                    st.session_state["ai_product_name"] = selected_product
                except Exception as e:
                    st.error(f"AI generation failed: {e}")

        if st.session_state.get("ai_summary") and st.session_state.get("ai_product_name") == selected_product:
            ai_text = st.session_state["ai_summary"]
            st.markdown("---")
            if st.button("📄 Build PDF Report"):
                buffer = io.BytesIO()
                doc    = SimpleDocTemplate(buffer, rightMargin=inch, leftMargin=inch,
                                           topMargin=inch, bottomMargin=inch)
                styles    = getSampleStyleSheet()
                body_style = ParagraphStyle("body", parent=styles["Normal"],
                                            fontSize=11, leading=16, spaceAfter=12)
                data = [
                    ["Metric", "Value"],
                    ["Total Reviews",       str(total_reviews)],
                    ["Positive Reviews",    f"{positive_reviews} ({positive_pct:.1f}%)"],
                    ["Negative Reviews",    f"{negative_reviews} ({negative_pct:.1f}%)"],
                    ["Overall Health Score",f"{health_score:.1f}"],
                ]
                tbl = Table(data, colWidths=[3 * inch, 3 * inch])
                tbl.setStyle(TableStyle([
                    ("BACKGROUND",     (0, 0), (-1, 0), rl_colors.HexColor("#1d4ed8")),
                    ("TEXTCOLOR",      (0, 0), (-1, 0), rl_colors.white),
                    ("GRID",           (0, 0), (-1, -1), 0.5, rl_colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [rl_colors.HexColor("#f8fafc"), rl_colors.white]),
                    ("FONTSIZE",       (0, 0), (-1, -1), 10),
                    ("PADDING",        (0, 0), (-1, -1), 8),
                ]))
                elements = [
                    Paragraph("Product Intelligence Executive Report", styles["Heading1"]),
                    Paragraph(f"Product: {selected_product}", styles["Heading2"]),
                    Spacer(1, 0.3 * inch),
                    Paragraph("Key Metrics", styles["Heading3"]),
                    tbl,
                    Spacer(1, 0.3 * inch),
                    Paragraph("AI Executive Summary", styles["Heading3"]),
                    Paragraph(ai_text.replace("\n", "<br/>"), body_style)
                ]
                doc.build(elements)
                st.download_button(
                    label="📥 Download PDF",
                    data=buffer.getvalue(),
                    file_name=f"{selected_product}_Intelligence_Report.pdf",
                    mime="application/pdf"
                )

    # ── Tab 2: Natural Language Search ───────────────────
    with tab2:
        st.markdown("### 💬 Ask anything about your products")
        st.markdown("Type a plain English question and get an AI answer backed by your actual data.")
        st.caption("Try: *Which products have the most delivery complaints?* · *What are customers saying about Hockey Stick?* · *Which product should I fix first?*")

        nl_query = st.text_input(
            "Your question",
            placeholder="e.g. Which products have delivery issues?",
            key="nl_input"
        )

        if st.button("🔍 Get Answer", key="nl_btn") and nl_query:
            with st.spinner("Analysing your data..."):
                try:
                    summary_context = product_summary[[
                        "ProductName", "Total Reviews", "Overall Health Score",
                        "Positive Review Percentage (%)", "Negative Review Percentage (%)",
                        "Average Sentiment Score"
                    ]].to_string(index=False)

                    issue_context = (
                        df[df["DetectedIssue"] != "No Issue Detected"]
                        .groupby(["ProductName", "DetectedIssue"])
                        .size()
                        .reset_index(name="Count")
                        .sort_values("Count", ascending=False)
                        .head(40)
                        .to_string(index=False)
                    )

                    nl_prompt = f"""You are a marketing analytics AI assistant. Answer the user's question using ONLY the data below. Be specific — cite product names and numbers. Keep the answer concise (3-5 sentences max, or a short list if needed).

PRODUCT SUMMARY:
{summary_context}

TOP ISSUE COUNTS BY PRODUCT:
{issue_context}

QUESTION: {nl_query}

Answer directly and factually from the data above."""

                    client  = Groq()
                    nl_text = ""
                    nl_placeholder = st.empty()

                    stream = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        max_tokens=600,
                        messages=[{"role": "user", "content": nl_prompt}],
                        stream=True
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            nl_text += delta
                            nl_placeholder.markdown(
                                f'<div class="nl-card">{nl_text}</div>',
                                unsafe_allow_html=True
                            )

                    if "nl_history" not in st.session_state:
                        st.session_state["nl_history"] = []
                    st.session_state["nl_history"].append({"q": nl_query, "a": nl_text})

                except Exception as e:
                    st.error(f"Query failed: {e}")

        # Previous questions history
        history = st.session_state.get("nl_history", [])
        if len(history) > 1:
            st.markdown("---")
            st.markdown("#### 🕘 Previous Questions")
            for item in reversed(history[:-1]):
                with st.expander(f"Q: {item['q']}"):
                    st.markdown(item["a"])