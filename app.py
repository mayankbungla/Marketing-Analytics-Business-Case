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
summary_row = product_summary[product_summary["ProductName"] == selected_product].iloc[0]

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
# SECTION 3 — ROOT CAUSE ANALYSIS (Complaint Distribution )
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
# SECTION 4 — PRODUCTION-READY STRATEGIC RECOMMENDATIONS
# ----------------------------------------------------------

st.header("🧠 Strategic Business Recommendations")

# --- GROWTH & SCALING STRATEGY BUTTON ---
if st.button("🚀 Reveal Growth & Scaling Strategies"):
    st.subheader(f"Growth Playbook for: {selected_product}")
    
    growth_playbook = {
        "Climbing Rope": [
            "**Summit Socials:** Launch a campaign where users tag their climbing milestones; the best monthly photo wins a branded gear bag.",
            "**Adventure Bundling:** Partner with local climbing gyms to offer a 'Gym-to-Crag' starter pack (Rope + Chalk Bag).",
            "**Safety Authority:** Host live monthly streams on safety knots and rope maintenance to build expert brand trust."
        ],
        "Basketball": [
            "**Streetball Sponsorship:** Sponsor local 3v3 weekend tournaments to get the ball into the hands of real competitive players.",
            "**Coach's Bulk Choice:** Offer specialized 'Team Pricing' for high school and youth league coaches for official practice balls.",
            "**Trick Shot Viral:** Run a TikTok challenge for the most creative trick shot, rewarding the winner with a professional jersey."
        ],
        "Ski Boots": [
            "**Fit-First Campaign:** Partner with ski resorts to offer 'Free Fit Trials' where guests test the boots for an hour.",
            "**Pro-Athlete Endorsement:** Sponsor regional winter athletes to showcase the boots' durability in extreme conditions.",
            "**Seasonal Pre-Order:** Offer a 15% 'Early Bird' discount for pre-orders placed in late summer to manage inventory better."
        ],
        "Ice Skates": [
            "**Rink Partnerships:** Become the 'Official Skate' for local community rinks, offering discounted rentals of your brand.",
            "**Performance Clinics:** Sponsor free basic skating lessons at public rinks led by pros wearing your gear.",
            "**Beginner-to-Pro Path:** Launch a trade-in program where customers can upgrade to a pro model as their skills improve."
        ],
        "Kayak": [
            "**Eco-Explorer Series:** Sponsor local river cleanup events, providing kayaks for volunteers to increase brand visibility.",
            "**Lake Day Pop-ups:** Set up demo tents at popular weekend lake destinations for free 15-minute trial paddles.",
            "**Strap-and-Go Bundle:** Sell a discounted bundle that includes a roof rack and safety vest with every kayak purchase."
        ],
        "Football Helmet": [
            "**Safety First Certification:** Partner with youth leagues to provide safety seminars on proper helmet fitting and impact protection.",
            "**Team Customization:** Offer free team-logo decals for bulk orders of 20+ helmets for local junior football clubs.",
            "**Impact Tech Ads:** Create video content focusing on the internal shock-absorption technology to justify premium pricing."
        ],
        "Swim Goggles": [
            "**Clear-Vision Guarantee:** Market a 'No-Fog' 90-day guarantee to differentiate from cheaper, low-quality competitors.",
            "**Swim School Supply:** Partner with indoor swim schools to be the recommended brand for new student starter kits.",
            "**Anti-Chlorine Bundle:** Cross-sell with high-quality swim caps or anti-chlorine shampoo to increase average order value."
        ],
        "Cycling Helmet": [
            "**Commuter Safety Blitz:** Run ads targeted at city commuters emphasizing the aerodynamic design and visibility lights.",
            "**Bike Shop Network:** Set up 'Safety Kiosks' in boutique bike shops with QR codes for instant online ordering.",
            "**Night-Rider Series:** Release a limited edition high-visibility color line for night cyclists and urban commuters."
        ],
        "Fitness Tracker": [
            "**Corporate Challenges:** Pitch bulk-buy deals to HR departments for 'Employee Health Month' step-tracking challenges.",
            "**Influencer Sync:** Send units to marathon pacers and fitness coaches for 'Day in the Life' battery-life reviews.",
            "**Leaderboard Perks:** Create an app-based community where the top 10% of monthly active users get 20% off accessories."
        ],
        "Tennis Racket": [
            "**Demo Days:** Host 'Try Before You Buy' events at local tennis clubs, providing rackets for weekend round-robins.",
            "**Pro-Stringing Service:** Offer 3 months of free restringing at partner shops with every professional-grade racket sale.",
            "**Junior Development:** Sponsor local youth tennis camps and provide rackets for the 'Most Improved Player' awards."
        ],
        "Running Shoes": [
            "**Run Club Rewards:** Sponsor local Saturday morning run clubs with free water, snacks, and shoe trial opportunities.",
            "**Marathon Pop-up:** Set up a recovery station at major local marathons where runners can try on the latest recovery footwear.",
            "**Mileage Milestones:** Launch an app feature that gives customers a discount on their next pair once they hit 500 miles."
        ],
        "Golf Clubs": [
            "**Driving Range Demos:** Set up a permanent 'Demo Bag' at premium driving ranges for golfers to test during practice.",
            "**Lessons Bundle:** Partner with PGA pros to include a 1-hour coaching session with every full set purchase.",
            "**Virtual Fitting:** Offer a free Zoom/Teams call with a fitting expert to help customers choose the right shaft stiffness."
        ],
        "Yoga Mat": [
            "**Studio Affiliate:** Give local yoga studios an affiliate code to earn a commission for every student that buys a mat.",
            "**Sustainable Story:** Highlight the eco-friendly materials in 'Nature-Focused' ads on Pinterest and Instagram.",
            "**Free Flow Classes:** Host free outdoor community yoga sessions where participants can rent and test the mats."
        ],
        "Dumbbells": [
            "**Home Gym Blueprint:** Create downloadable 'Home Workout PDF Guides' that are unlocked via a QR code on the weights.",
            "**Weight-Up Program:** Offer a discount on the next weight class (e.g., 20lb) once the customer buys the current set (15lb).",
            "**Compact Living Ads:** Target apartment dwellers with ads showing the space-saving design and floor-protection coating."
        ],
        "Baseball Glove": [
            "**Break-In Service:** Offer a premium 'Professional Steam & Break-in' service with every high-end leather glove sale.",
            "**Little League Day:** Sponsor the opening day of local youth leagues with a 'Gold Glove' pop-up tent for sizing.",
            "**Personalized Stitching:** Offer free name/number embroidery for a limited time to make the product a perfect gift."
        ],
        "Volleyball": [
            "**Beach Tourney Title:** Become the 'Official Ball' for regional beach volleyball circuits to gain pro-level visibility.",
            "**Club Connection:** Offer discounted bulk pricing for club volleyball teams for their practice and travel ball sets.",
            "**Skill Tutorials:** Create a YouTube series on 'How to serve with power' featuring the product to drive organic search."
        ],
        "Surfboard": [
            "**Surf School Lease:** Provide surf schools with boards for lessons in exchange for 'On-Site' branding and rental priority.",
            "**Shaper Series:** Feature videos of the designers explaining the board's 'rocker' and 'volume' to appeal to enthusiast surfers.",
            "**Eco-Wax Bundle:** Include a bar of organic, eco-friendly surf wax with every board to build brand lifestyle affinity."
        ],
        "Soccer Ball": [
            "**Street Skills Contest:** Launch an Instagram 'Freestyle' contest where users show off their best juggles with your ball.",
            "**Futsal Expansion:** Market a specific 'Low-Bounce' version of your ball for the rapidly growing indoor futsal market.",
            "**Goalie's Nightmare:** Create high-speed video ads showing the ball's flight stability and curve potential to excite strikers."
        ],
        "Boxing Gloves": [
            "**Gym Starter Kit:** Bundle gloves with hand wraps and a jump rope as a 'Day 1' kit for people joining boxing gyms.",
            "**Sparring Partner Program:** Offer discounts to gym owners who replace their old 'house gloves' with your brand.",
            "**Durability Challenge:** Post 'Stress-Test' videos showing the gloves hitting heavy bags for 100+ rounds without tearing."
        ],
        "Hockey Stick": [
            "**Ice-Trial Nights:** Sponsor 'Public Skate' nights where players can take 10 shots on net with the latest stick model.",
            "**Taped-Up Style:** Sell branded, high-grip stick tape in the box to add extra value and brand loyalty.",
            "**Flex-Fit Guide:** Create an online calculator that recommends the perfect stick 'flex' based on a player's height and weight."
        ]
    }
    
    # Fetch the selected product's strategies or a default fallback
    strategies = growth_playbook.get(selected_product, [
        "**UGC Ad Blitz:** Turn your best 5-star customer reviews into simple, high-energy video ads for Instagram.",
        "**VIP Early Access:** Give your repeat buyers a 24-hour head start on new stock or seasonal sales.",
        "**Refer-a-Friend:** Offer a 'Give 15%, Get 15%' discount code to turn your happy customers into a sales team."
    ])
    
    # Display the results
    for s in strategies:
        st.write(f"📈 {s}")
    st.markdown("---")

# --- ROOT CAUSE REMEDIATION (TOP 2 ISSUES) ---
# We filter out 'No Issue Detected' to address actual business problems
actual_issues = issue_counts[issue_counts["Issue Category"] != "No Issue Detected"]
top_two_issues = actual_issues.head(2)["Issue Category"].tolist()

recommendations = {
    "Delivery Issue": [
        "**Ship Faster:** Box and label orders within 12 hours so they beat the shipping backlog.",
        "**Smarter Shipping:** Use better courier companies for the cities where people complain about delays most.",
        "**Auto-Tracking:** Send a text the second the item leaves the warehouse so customers feel in control.",
        "**Late-Arrival Gift:** If a delivery is late, send an automatic 10% discount for their next purchase."
    ],
    "Product Quality": [
        "**Batch Audit:** Check the last 100 items for 'cheap' or 'faulty' materials before shipping the next lot.",
        "**Talk to Factory:** Share negative reviews directly with the manufacturer to demand higher durability.",
        "**Full Guarantee:** Market a 6-month 'No-Hassle' replacement policy to prove you trust your gear.",
        "**Premium Upgrade:** If customers say it feels thin, switch to a thicker material and slightly raise the price."
    ],
    "Pricing Issue": [
        "**Bundle Up:** Sell the product with a small, high-margin accessory to make the price feel like a bargain.",
        "**Price Matching:** Compare your prices weekly with competitors to ensure you aren't the most expensive.",
        "**Payment Plans:** Offer 'Klarna' or 'Afterpay' so larger gear costs less upfront for the customer.",
        "**Feature Shout-out:** Use your ads to explain why yours is better than the cheap versions (e.g., 'Lifetime warranty')."
    ],
    "Customer Service": [
        "**4-Hour Reply:** Set a goal to answer every angry email in under 4 hours to stop them from writing bad reviews.",
        "**Self-Help FAQ:** Add a 'Where is my order?' and 'How to return' chatbot to your site for instant answers.",
        "**Human Touch:** Have a manager personally email every 1-star reviewer to offer a fix or a refund.",
        "**Follow-Up Care:** 10 days after a sale, send a friendly check-in email to see if they need help with the setup."
    ],
    "Packaging Issue": [
        "**Double Box:** Use thicker boxes or more bubble wrap for shipping—it's cheaper than paying for returns.",
        "**Unboxing Glow-up:** Make the inside look premium. Clean tissue paper and a 'Thank You' card hide small flaws.",
        "**Eco-Sturdy:** Use recycled but thick cardboard that protects the gear while appealing to eco-conscious buyers.",
        "**Tear-Free:** Use 'Frustration-Free' packaging that opens easily without needing sharp knives."
    ],
    "Performance Issue": [
        "**User Videos:** Put a 30-second 'How to setup' video on the product page so people don't use it wrong.",
        "**Tech Audit:** If items are 'lagging' or 'overheating,' run an internal stress test on the current stock.",
        "**Software Update:** If it's a tech item, release a firmware patch to fix known bugs reported in reviews.",
        "**Expert Tips:** Send a weekly email with 'Pro Tips' on how to get the best performance out of the product."
    ],
    "Usability Issue": [
        "**Simplified Manual:** Rewrite your instructions so a 10-year-old can understand the setup in 3 steps.",
        "**QR Code Help:** Print a QR code on the box that links directly to a video assembly guide.",
        "**Quick-Start Card:** Put a giant 'Read This First' card on top of the product inside the box.",
        "**Community Board:** Create a website page where users can share their own tips and tricks for the product."
    ],
    "Expectation Gap": [
        "**Real-World Photos:** Add customer photos (not just studio shots) to the site so buyers know exactly what to expect.",
        "**Size Guide:** Add a photo of the product next to a common item (like a phone) so people understand the scale.",
        "**Be Honest:** If a product isn't 'Pro' grade, don't say it is. Market it as 'Great for Beginners' to lower complaints.",
        "**Comparison Table:** Clearly show the difference between your 'Standard' and 'Pro' models on the product page."
    ]
}

# --- DYNAMIC ACTION PLAN DISPLAY ---
if top_two_issues:
    st.subheader("🚩 Action Plan for Top Improvements")
    for issue in top_two_issues:
        if issue in recommendations:
            with st.expander(f"**Immediate Steps for: {issue}**", expanded=True):
                for r in recommendations[issue]:
                    st.write(f"• {r}")
else:
    st.success("✅ This product is a top performer! No major issues were detected in the data.")


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