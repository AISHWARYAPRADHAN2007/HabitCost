import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import io
from achievements import get_achievements
from calculations import financial_health_score
from auth import logout
from auth import get_user
from database import (
    supabase,
    get_habits,
    get_habit_logs,
    get_month_snapshots,
    get_all_habit_logs,
    get_saved_achievements,
    save_achievement,
    get_profile,
    save_profile,
    add_month_snapshot,
)
from recommendations import generate_recommendations
from calculations import monthly_cost

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)
if st.button(
    "🏠 Home",
    key="dashboard_home_button",
    use_container_width=False,
):
    st.switch_page("app.py")

def load_css():
    with open("assets/style.css", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )


load_css()


# ==========================================
# LOGIN
# ==========================================

if "user" not in st.session_state:
    st.session_state.user = get_user()


if st.session_state.user is None:
    st.warning("Please login first.")
    st.stop()


user_email = st.session_state.user.email
if "session" in st.session_state and st.session_state.session:

    try:
        supabase.auth.set_session(
            st.session_state.session.access_token,
            st.session_state.session.refresh_token,
        )

    except Exception as e:
        st.warning("Session expired. Please login again.")
        st.stop()
profile = get_profile(user_email)

habits = get_habits(user_email)

home_df = pd.DataFrame(habits)

# ==========================================
# LOAD HABITS
# ==========================================

habits = get_habits(user_email)

df = pd.DataFrame(habits)


if df.empty:

    st.info(
        "No habits added yet. Add habits first!"
    )

    st.stop()



# ==========================================
# CALCULATIONS
# ==========================================

df["monthly_cost"] = df.apply(
    lambda row: monthly_cost(
        row["cost"],
        row["frequency"]
    ),
    axis=1
)


total_monthly_spending = df["monthly_cost"].sum()


total_habits = len(df)


top_category = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .idxmax()
)


top_category_amount = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .max()
)



# ==========================================
# TITLE
# ==========================================

st.markdown(
    """
<div class="dashboard-page-header"><div class="dashboard-page-eyebrow">FINANCIAL INSIGHTS</div><div class="dashboard-page-title">📊 Financial Dashboard</div><div class="dashboard-page-subtitle">Understand where your money goes and how your habits shape your financial future.</div></div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# TOP SUMMARY CARDS
# ==========================================



st.markdown("### Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
<div class="dashboard-metric dashboard-metric-orange"><div class="dashboard-metric-icon">💸</div><div class="dashboard-metric-label">Monthly Spending</div><div class="dashboard-metric-value">₹ {total_monthly_spending:,.0f}</div><div class="dashboard-metric-note">Estimated monthly impact</div></div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
<div class="dashboard-metric dashboard-metric-blue"><div class="dashboard-metric-icon">📌</div><div class="dashboard-metric-label">Habits Tracked</div><div class="dashboard-metric-value">{total_habits}</div><div class="dashboard-metric-note">Active spending habits</div></div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
<div class="dashboard-metric dashboard-metric-purple"><div class="dashboard-metric-icon">🔥</div><div class="dashboard-metric-label">Biggest Category</div><div class="dashboard-metric-value dashboard-metric-text">{top_category}</div><div class="dashboard-metric-note">Largest spending category</div></div>
""",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
<div class="dashboard-metric dashboard-metric-green"><div class="dashboard-metric-icon">💰</div><div class="dashboard-metric-label">Category Cost</div><div class="dashboard-metric-value">₹ {top_category_amount:,.0f}</div><div class="dashboard-metric-note">Monthly category total</div></div>
""",
        unsafe_allow_html=True,
    )

# ==========================================
# MONTHLY SNAPSHOT
# ==========================================
# ==========================================
# MONTHLY SNAPSHOT
# ==========================================

st.markdown(
    """
<div class="section-header">
    <div class="section-title">📅 Monthly Snapshot</div>
    <div class="section-subtitle">
        Save a summary of your current month's financial habits for future comparison.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

with st.container(key="snapshot_section"):
    
    
    if "snapshot_saved" not in st.session_state:
        st.session_state.snapshot_saved = False


    if st.session_state.snapshot_saved:
        st.success("✅ Monthly snapshot saved successfully!")
        st.session_state.snapshot_saved = False


    if st.button(
    "💾 Save Monthly Snapshot",
    use_container_width=True,
    key="snapshot_button",

    ):

        add_month_snapshot(
            user_email,
            datetime.now().strftime("%B %Y"),
            float(total_monthly_spending),
            top_category,
            int(total_habits),
        )

        st.session_state.snapshot_saved = True
        st.rerun()
        
    
    

# ==========================================
# FINANCIAL HEALTH SCORE
# ==========================================

# ==========================================
# FINANCIAL HEALTH SCORE
# ==========================================
st.markdown('<div class="dashboard-section-card">', unsafe_allow_html=True)
st.subheader("🧠 Financial Health Score")

subscription_cost = (
    df[
        df["category"] == "Subscriptions"
    ]["monthly_cost"]
    .sum()
)

score = 100

st.markdown("</div>", unsafe_allow_html=True)


# Budget overspending penalty


# Budget overspending penalty


monthly_budget = 0

if profile:
    monthly_budget = profile.get("monthly_budget", 0)

    if monthly_budget is None:
        monthly_budget = 0

if monthly_budget > 0:

    budget_usage = (
        total_monthly_spending / monthly_budget
    )

    if budget_usage > 3:
        score -= 50

    elif budget_usage > 2:
        score -= 35

    elif budget_usage > 1:
        score -= 20

# High spending penalty
if total_monthly_spending > 50000:
    score -= 15

elif total_monthly_spending > 20000:
    score -= 5


# Habit tracking bonus
if total_habits >= 5:
    score += 5


# Subscription penalty
if subscription_cost > 3000:
    score -= 10


score = max(0, min(score,100))

col1, col2 = st.columns([1.2, 1])

with col1:

    if score >= 80:
        color = "#22C55E"
        status = "Excellent"
        emoji = "🟢"

    elif score >= 60:
        color = "#F59E0B"
        status = "Good"
        emoji = "🟡"

    else:
        color = "#EF4444"
        status = "Needs Attention"
        emoji = "🔴"

    st.markdown(
        f"""
<div class="health-card">
    <div class="health-score" style="color:{color};">{score}</div>
    <div class="health-outof">/100</div>
    <div class="health-status">{emoji} {status}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:

    st.markdown(
        f"""
<div class="health-info">
<h4>Financial Health</h4>

<p>Your score is calculated using:</p>

<ul>
<li>Monthly spending</li>
<li>Budget utilization</li>
<li>Subscription costs</li>
<li>Habit tracking consistency</li>
</ul>

</div>
""",
        unsafe_allow_html=True,
    )


    
# ==========================================
# MONTHLY BUDGET TRACKER
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">📅 Monthly Budget Tracker</div><div class="section-subtitle">Set a monthly limit and track how much of your budget has already been used.</div></div>
""",
    unsafe_allow_html=True,
)

profile = get_profile(user_email)

current_budget = 0

if profile:
    current_budget = profile.get("monthly_budget", 0)

    if current_budget is None:
        current_budget = 0

new_budget = st.number_input(
    "Set Monthly Budget",
    min_value=0,
    value=int(current_budget)
)


if st.button("Save Budget"):
    
    save_profile(
        user_email,
        profile.get("income", 0),
        profile.get("currency", "INR"),
        profile.get("investment_rate", 12),
        new_budget,
        profile.get("goal", ""),
        profile.get("notes", "")
    )

    st.success("Budget updated!")

    st.rerun()

    st.rerun()



if new_budget > 0:

    spent = total_monthly_spending


    remaining = (
        new_budget - spent
    )


    progress = (
        spent / new_budget
    )

    st.markdown("### Budget Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
    <div class="budget-card budget-blue">
        <div class="budget-label">💳 Budget</div>
        <div class="budget-value">₹ {new_budget:,.0f}</div>
    </div>
    """,
            unsafe_allow_html=True,
       )

    with col2:
        st.markdown(
           f"""
    <div class="budget-card budget-orange">
        <div class="budget-label">💸 Spent</div>
        <div class="budget-value">₹ {spent:,.0f}</div>
    </div>
    """,
           unsafe_allow_html=True,
       )

    with col3:
        st.markdown(
           f"""
    <div class="budget-card budget-green">
        <div class="budget-label">💚 Remaining</div>
        <div class="budget-value">₹ {remaining:,.0f}</div>
    </div>
    """,
            unsafe_allow_html=True,
       )

    st.markdown(
       f"""
    <div class="budget-progress-header">
       <span>Budget Used</span>
       <span>{min(progress*100,100):.0f}%</span>
    </div>
    """,
       unsafe_allow_html=True,
    )

    st.progress(min(progress, 1.0))

# ==========================================
# ACHIEVEMENTS
# ==========================================
st.markdown('<div class="dashboard-section-card">', unsafe_allow_html=True)

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">🏆 Achievements</div><div class="section-subtitle">Unlock milestones as you track habits, control spending, and improve your financial discipline.</div></div>
""",
    unsafe_allow_html=True,
)

all_logs = get_all_habit_logs(
    user_email
)

total_logs = len(all_logs)


achievements = get_achievements(
    total_habits,
    total_logs,
    total_monthly_spending,
    new_budget
)


saved = get_saved_achievements(
    user_email
)


saved_names = [
    item["achievement_name"]
    for item in saved
]


achievement_cols = st.columns(3)


index = 0


for badge in achievements:

    with achievement_cols[index % 3]:

        if badge["unlocked"]:

            if badge["title"] not in saved_names:

                save_achievement(
                    user_email,
                    badge["title"]
                )


            st.markdown(
                f"""
            <div class="achievement-card achievement-unlocked">
                <div class="achievement-icon">🏆</div>
                <div class="achievement-title">{badge['title']}</div>
                <div class="achievement-description">{badge['description']}</div>
                <div class="achievement-badge">UNLOCKED ✓</div>
            </div>
            """,
               unsafe_allow_html=True,
            )

        else:

            st.markdown(
                f"""
            <div class="achievement-card achievement-locked">
                <div class="achievement-icon">🔒</div>
                <div class="achievement-title">{badge['title']}</div>
                <div class="achievement-description">{badge['description']}</div>
                <div class="achievement-badge locked">LOCKED</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
    index += 1
st.markdown("</div>", unsafe_allow_html=True) 

# ==========================================
# PERSONALIZED RECOMMENDATIONS
# ==========================================
st.markdown('<div class="dashboard-section-card">', unsafe_allow_html=True)
st.divider()

st.subheader(
    "🤖 Personalized Recommendations"
)


st.caption(
    "Smart suggestions based on your spending habits."
)

goal = profile.get("goal", "Save More") if profile else "Save More"

recommendations = generate_recommendations(
    habits,
    total_monthly_spending,
    new_budget,
    goal,
)
    
for rec in recommendations:

    if rec["type"] == "warning":
        card_class = "recommendation-warning"
        icon = "💡"
        title = "Money Saving Tip"

    elif rec["type"] == "success":
        card_class = "recommendation-success"
        icon = "🎯"
        title = "Smart Move"

    elif rec["type"] == "danger":
        card_class = "recommendation-danger"
        icon = "🚨"
        title = "Attention Needed"

    else:
        card_class = "recommendation-info"
        icon = "📌"
        title = "Recommendation"

    st.markdown(
        f"""
<div class="recommendation-card {card_class}"><div class="recommendation-icon">{icon}</div><div class="recommendation-content"><div class="recommendation-title">{title}</div><div class="recommendation-message">{rec['message']}</div></div></div>
""",
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# ANALYTICS PREVIEW
# ==========================================
st.markdown('<div class="dashboard-section-card">', unsafe_allow_html=True)
st.divider()

st.subheader("📈 Analytics Preview")

preview_col1, preview_col2 = st.columns([2, 1])

with preview_col1:

    category_preview = (
        df.groupby("category")["monthly_cost"]
        .sum()
        .sort_values(ascending=False)
    )

    preview_df = (
        category_preview.reset_index()
    )

    preview_df.columns = [
        "Category",
        "Monthly Cost"
    ]

    fig = px.bar(
        preview_df,
        x="Category",
        y="Monthly Cost",
        color="Monthly Cost",
        text_auto=".0f",
        color_continuous_scale=[
        "#3B82F6",
        "#8B5CF6",
        "#F97316",
        ],
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),

        font=dict(
        color="#E2E8F0",
        family="Inter"
        ),

        coloraxis_showscale=False,

        xaxis_title="",
        yaxis_title="",
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,.08)",
        zeroline=False,
    )

    fig.update_traces(
        marker_line_width=0,
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with preview_col2:

    st.markdown(
        f"""
    <div class="analytics-side-card analytics-blue">
        <div class="analytics-label">🏆 Top Category</div>
        <div class="analytics-value">{top_category}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="analytics-side-card analytics-green">
        <div class="analytics-label">💰 Monthly Cost</div>
        <div class="analytics-value">₹ {top_category_amount:,.0f}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="analytics-note">
       📈 Explore the Analytics page for detailed trends, category insights, and spending patterns.
    </div>
    """,
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)
# ==========================================
# SPENDING VISUALIZATION
# ==========================================
st.markdown('<div class="dashboard-section-card">', unsafe_allow_html=True)
st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">📊 Spending Insights</div><div class="section-subtitle">Visual breakdown of your monthly expenses across categories.</div></div>
""",
    unsafe_allow_html=True,
)

category_chart = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .reset_index()
)

category_chart.columns = [
    "Category",
    "Monthly Cost"
]

col1, col2 = st.columns(2)

with col1:

    fig = px.bar(
    category_chart,
    x="Category",
    y="Monthly Cost",
    color="Monthly Cost",
    text_auto=".0f",
    color_continuous_scale=[
        "#3B82F6",
        "#8B5CF6",
        "#F97316",
    ],
    )

    fig.update_layout(
    title="Monthly Spending by Category",
    title_font=dict(
        size=21,
        color="#F8FAFC",
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="#CBD5E1",
    ),
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20,
    ),
    xaxis_title=None,
    yaxis_title="Monthly Cost",
    coloraxis_showscale=False,
    hoverlabel=dict(
        bgcolor="#0F172A",
        font_color="#F8FAFC",
    ),
    )

    fig.update_xaxes(
    showgrid=False,
    zeroline=False,
    tickfont=dict(
        color="#CBD5E1",
    ),
    )

    fig.update_yaxes(
    gridcolor="rgba(255,255,255,0.08)",
    zeroline=False,
    tickprefix="₹ ",
    tickfont=dict(
        color="#94A3B8",
    ),
    )

    fig.update_traces(
    marker_line_width=0,
    texttemplate="₹ %{y:,.0f}",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Monthly Cost: ₹ %{y:,.0f}"
        "<extra></extra>"
    ),
    )

    st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
    )

with col2:

    fig = px.pie(
        category_chart,
        names="Category",
        values="Monthly Cost",
        hole=0.66,
        color_discrete_sequence=[
            "#8B5CF6",
            "#3B82F6",
            "#22C55E",
            "#F97316",
            "#EF4444",
            "#06B6D4",
            "#FACC15",
            "#EC4899",
        ],
    )

    fig.update_layout(
        title="Spending Distribution",
        title_font=dict(
            size=21,
            color="#F8FAFC",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#CBD5E1",
        ),
        margin=dict(
            l=15,
            r=15,
            t=60,
            b=20,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(
                color="#CBD5E1",
                size=12,
            ),
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_color="#F8FAFC",
        ),
    )

    fig.update_traces(
        textinfo="percent",
        textposition="inside",
        textfont=dict(
            color="#F8FAFC",
            size=13,
        ),
        marker=dict(
            line=dict(
                color="#0F172A",
                width=3,
            ),
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Monthly Cost: ₹ %{value:,.0f}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )
st.markdown("</div>", unsafe_allow_html=True)
# ==========================================
# TOP SAVINGS OPPORTUNITIES
# ==========================================
st.markdown('<div class="dashboard-section-card">', unsafe_allow_html=True)
st.divider()

st.subheader("💡 Top Savings Opportunities")

top_habits = (
    df.sort_values("monthly_cost", ascending=False)
    .head(5)
)

display_df = top_habits[
    ["habit", "category", "monthly_cost"]
].copy()

display_df.columns = [
    "Habit",
    "Category",
    "Monthly Saving Potential"
]

display_df["Monthly Saving Potential"] = display_df[
    "Monthly Saving Potential"
].map(lambda x: f"₹ {x:,.0f}")

st.markdown(
    """
<div class="section-header">
    <div class="section-title">💡 Top Saving Opportunities</div>
    <div class="section-subtitle">
        Habits with the highest monthly saving potential.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

for i, row in display_df.iterrows():

    st.markdown(
        f"""
<div class="saving-row"><div class="saving-rank">#{i+1}</div><div class="saving-main"><div class="saving-habit">{row['Habit']}</div><div class="saving-category">{row['Category']}</div></div><div class="saving-amount">{row['Monthly Saving Potential']}</div></div>
""",
        unsafe_allow_html=True,
    )
highest = top_habits.iloc[0]

st.markdown(
    f"""
<div class="featured-saving">

<div class="featured-title">
💰 Biggest Saving Opportunity
</div>

<div class="featured-text">
Reducing <b>{highest['habit']}</b> by just <b>50%</b> could save approximately
<b>₹ {highest['monthly_cost']/2:,.0f}</b> every month.
</div>

<div class="featured-footer">
See the Investments page to estimate long-term growth.
</div>

</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="dashboard-footer"><div class="footer-brand">💸 HabitCost</div><div class="footer-tagline">Track • Improve • Invest</div><div class="footer-note">Built with Streamlit and Supabase</div></div>
""",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
