import streamlit as st
import pandas as pd
import plotly.express as px
from auth import logout


from auth import get_user
from database import (
    supabase,
    get_habits,
    get_month_snapshots,
)
from calculations import monthly_cost

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Analytics",
    page_icon="📈",
    layout="wide"
)

def load_css():
    with open("assets/style.css", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )


load_css()



if st.button(
    "🏠 Home",
    key="analytics_home_button",
):
    st.switch_page("app.py")



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

    except Exception:
        
        st.warning("Session expired. Please login again.")

        st.stop()



# ==========================================
# LOAD DATA
# ==========================================

habits = get_habits(
    user_email
)


df = pd.DataFrame(
    habits
)


if df.empty:

    st.info(
        "Add habits first to see analytics."
    )

    st.stop()



df["monthly_cost"] = df.apply(
    lambda row: monthly_cost(
        row["cost"],
        row["frequency"]
    ),
    axis=1
)



# ==========================================
# TITLE
# ==========================================

st.markdown(
    """
<div class="analytics-page-header"><div class="analytics-page-eyebrow">SPENDING INTELLIGENCE</div><div class="analytics-page-title">📈 Analytics</div><div class="analytics-page-subtitle">Explore your spending patterns, compare habit impact, and track how your monthly costs change over time.</div></div>
""",
    unsafe_allow_html=True,
)

category_data = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .sort_values(
        ascending=False
    )
)



total_monthly = df["monthly_cost"].sum()

highest_habit = df.loc[
    df["monthly_cost"].idxmax(),
    "habit"
]

highest_cost = df["monthly_cost"].max()

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
<div class="analytics-summary-card analytics-summary-blue"><div class="analytics-summary-icon">💳</div><div class="analytics-summary-content"><div class="analytics-summary-label">Monthly Spending</div><div class="analytics-summary-value">₹ {total_monthly:,.0f}</div><div class="analytics-summary-note">Estimated total each month</div></div></div>
""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
<div class="analytics-summary-card analytics-summary-purple"><div class="analytics-summary-icon">🗂️</div><div class="analytics-summary-content"><div class="analytics-summary-label">Categories</div><div class="analytics-summary-value">{len(category_data)}</div><div class="analytics-summary-note">Spending categories tracked</div></div></div>
""",
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
<div class="analytics-summary-card analytics-summary-orange"><div class="analytics-summary-icon">🔥</div><div class="analytics-summary-content"><div class="analytics-summary-label">Costliest Habit</div><div class="analytics-summary-value analytics-summary-habit">{highest_habit}</div><div class="analytics-summary-note">₹ {highest_cost:,.0f} per month</div></div></div>
""",
        unsafe_allow_html=True,
    )

# ==========================================
# SPENDING BY CATEGORY
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">💸 Spending by Category</div><div class="section-subtitle">See which categories consume the largest share of your monthly budget.</div></div>
""",
    unsafe_allow_html=True,
)



chart_col, info_col = st.columns([2, 1])

with chart_col:
    category_chart = category_data.reset_index()

    category_chart.columns = [
        "Category",
        "Monthly Cost",
    ]

    fig = px.bar(
        category_chart,
        x="Category",
        y="Monthly Cost",
        color="Monthly Cost",
        color_continuous_scale=[
            "#3B82F6",
            "#8B5CF6",
            "#F59E0B",
        ],
        text="Monthly Cost",
    )

    fig.update_traces(
        texttemplate="₹ %{text:,.0f}",
        textposition="outside",
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>₹ %{y:,.0f} per month<extra></extra>",
    )

    fig.update_layout(
        height=450,
        margin=dict(
            l=10,
            r=10,
            t=30,
            b=10,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#CBD5E1",
        ),
        xaxis=dict(
            title="",
            showgrid=False,
            tickfont=dict(
                color="#CBD5E1",
            ),
        ),
        yaxis=dict(
            title="Monthly Cost (₹)",
            gridcolor="rgba(148,163,184,0.12)",
            zeroline=False,
            tickprefix="₹ ",
            tickformat=",",
        ),
        coloraxis_showscale=False,
        bargap=0.32,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

with info_col:
    highest_category = category_data.idxmax()
    highest_amount = category_data.max()

    st.markdown(
        f"""
<div class="category-insight-card category-top-card"><div class="category-insight-icon">🏆</div><div class="category-insight-label">Top Spending Category</div><div class="category-insight-value">{highest_category}</div><div class="category-insight-amount">₹ {highest_amount:,.0f} / month</div></div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="category-breakdown-heading">📌 Category Breakdown</div>
""",
        unsafe_allow_html=True,
    )

    for category, amount in category_data.items():
        percentage = amount / category_data.sum() * 100

        st.markdown(
            f"""
<div class="category-progress-header"><span>{category}</span><span>{percentage:.1f}%</span></div>
""",
            unsafe_allow_html=True,
        )

        st.progress(
            percentage / 100,
        )


# ==========================================
# HABIT IMPACT
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">🔥 Habit Impact Comparison</div><div class="section-subtitle">Compare the monthly and yearly financial impact of every habit across each category.</div></div>
""",
    unsafe_allow_html=True,
)


impact_df = df.copy()

impact_df["yearly_cost"] = (
    impact_df["monthly_cost"] * 12
)


category_icons = {
    "Food": "🍔",
    "Transport": "🚗",
    "Entertainment": "🎬",
    "Shopping": "🛍️",
    "Health": "💪",
    "Subscriptions": "📺",
    "Education": "📚",
    "Other": "💸",
}


categories = impact_df["category"].unique()


for category in categories:

    category_df = impact_df[
        impact_df["category"] == category
    ]


    monthly_total = (
        category_df["monthly_cost"].sum()
    )


    yearly_total = monthly_total * 12


    st.markdown(
        f"""
    <div class="habit-impact-header"><div class="habit-impact-title">{category_icons.get(category, "💸")} {category}</div><div class="habit-impact-stats"><div><span>Monthly</span><strong>₹ {monthly_total:,.0f}</strong></div><div><span>Yearly</span><strong>₹ {yearly_total:,.0f}</strong></div></div></div>
    """,
        unsafe_allow_html=True,
    )
    category_df = category_df.sort_values(
        "yearly_cost",
        ascending=False
    )

    table_df = category_df[
        [
            "habit",
            "monthly_cost",
            "yearly_cost"
        ]
    ].copy()


    table_df = table_df.rename(
        columns={
            "habit":"Habit",
            "monthly_cost":"Monthly Cost",
            "yearly_cost":"Yearly Cost"
        }
    )
    
    table_df["Monthly Cost"] = table_df["Monthly Cost"].map(
    lambda x: f"₹ {x:,.0f}"
    ) 

    table_df["Yearly Cost"] = table_df["Yearly Cost"].map(
    lambda x: f"₹ {x:,.0f}"
    )

    for rank, (_, row) in enumerate(table_df.iterrows(), start=1):
        st.markdown(
            f"""
    <div class="habit-impact-row"><div class="habit-impact-rank">{rank}</div><div class="habit-impact-main"><div class="habit-impact-name">{row["Habit"]}</div><div class="habit-impact-monthly">{row["Monthly Cost"]} per month</div></div><div class="habit-impact-yearly">{row["Yearly Cost"]}<span>per year</span></div></div>
    """,
            unsafe_allow_html=True,
       )


st.divider()



# ==========================================
# SPENDING BREAKDOWN
# ==========================================


st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">📊 Spending Breakdown</div><div class="section-subtitle">Review how much each category contributes to your total monthly spending.</div></div>
""",
    unsafe_allow_html=True,
)

category_spending = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .sort_values(
        ascending=False
    )
)

for category, amount in category_spending.items():
    percentage = (
        amount / category_spending.sum() * 100
    )

    st.markdown(
        f"""
<div class="spending-breakdown-card"><div class="spending-breakdown-icon">{category_icons.get(category, "💸")}</div><div class="spending-breakdown-main"><div class="spending-breakdown-header"><div><div class="spending-breakdown-category">{category}</div><div class="spending-breakdown-note">{percentage:.1f}% of total spending</div></div><div class="spending-breakdown-amount">₹ {amount:,.0f}<span>/ month</span></div></div></div></div>
""",
        unsafe_allow_html=True,
    )

    st.progress(
        percentage / 100,
    )

# ==========================================
# HISTORY TRENDS
# ==========================================
st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">📈 Spending History</div><div class="section-subtitle">Track how your monthly spending changes over time and identify long-term trends.</div></div>
""",
    unsafe_allow_html=True,
)


snapshots = get_month_snapshots(
    user_email
)


if snapshots:
    history_df = pd.DataFrame(snapshots)

    history_df = history_df.sort_values(
        "month",
    )

    history_chart = history_df.rename(
        columns={
            "month": "Month",
            "spending": "Monthly Spending",
        }
    )

    latest_spending = history_chart.iloc[-1]["Monthly Spending"]

    if len(history_chart) > 1:
        previous_spending = history_chart.iloc[-2]["Monthly Spending"]
        spending_change = latest_spending - previous_spending
        spending_change_percent = (
            spending_change / previous_spending * 100
            if previous_spending
            else 0
        )
    else:
        spending_change = 0
        spending_change_percent = 0

    history_col, trend_col = st.columns([2, 1])

    with history_col:
        fig = px.line(
            history_chart,
            x="Month",
            y="Monthly Spending",
            markers=True,
        )

        fig.update_traces(
            line=dict(
                width=4,
                color="#3B82F6",
            ),
            marker=dict(
                size=9,
                color="#8B5CF6",
                line=dict(
                    width=2,
                    color="#F8FAFC",
                ),
            ),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.08)",
            hovertemplate="<b>%{x}</b><br>₹ %{y:,.0f}<extra></extra>",
        )

        fig.update_layout(
            height=450,
            margin=dict(
                l=10,
                r=10,
                t=30,
                b=10,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#CBD5E1",
            ),
            xaxis=dict(
                title="",
                showgrid=False,
                tickfont=dict(
                    color="#CBD5E1",
                ),
            ),
            yaxis=dict(
                title="Monthly Spending (₹)",
                gridcolor="rgba(148,163,184,0.12)",
                zeroline=False,
                tickprefix="₹ ",
                tickformat=",",
            ),
            hovermode="x unified",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    with trend_col:
        if spending_change > 0:
            trend_class = "history-trend-danger"
            trend_icon = "↗"
            trend_label = "Spending increased"
            trend_value = f"+₹ {spending_change:,.0f}"
        elif spending_change < 0:
            trend_class = "history-trend-success"
            trend_icon = "↘"
            trend_label = "Spending decreased"
            trend_value = f"-₹ {abs(spending_change):,.0f}"
        else:
            trend_class = "history-trend-neutral"
            trend_icon = "→"
            trend_label = "No spending change"
            trend_value = "₹ 0"

        st.markdown(
            f"""
<div class="history-latest-card"><div class="history-card-icon">📅</div><div class="history-card-label">Latest Monthly Spending</div><div class="history-card-value">₹ {latest_spending:,.0f}</div><div class="history-card-note">Most recent saved snapshot</div></div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
<div class="history-trend-card {trend_class}"><div class="history-trend-icon">{trend_icon}</div><div><div class="history-trend-label">{trend_label}</div><div class="history-trend-value">{trend_value}</div><div class="history-trend-percent">{abs(spending_change_percent):.1f}% compared with previous month</div></div></div>
""",
            unsafe_allow_html=True,
        )

else:
    st.markdown(
        """
<div class="history-empty-card"><div class="history-empty-icon">📊</div><div class="history-empty-title">No spending history yet</div><div class="history-empty-text">Save your first monthly snapshot from the Dashboard to begin tracking spending trends.</div></div>
""",
        unsafe_allow_html=True,
    )
    
st.markdown(
    """
<div class="analytics-footer"><div class="analytics-footer-brand">HabitCost Analytics</div><div class="analytics-footer-tagline">Small habits create measurable financial outcomes.</div><div class="analytics-footer-note">Your analytics update automatically whenever your habits or monthly snapshots change.</div></div>
""",
    unsafe_allow_html=True,
)