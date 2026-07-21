from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import streamlit as st
import pandas as pd
import io
from auth import logout
from auth import get_user
import plotly.express as px

from datetime import datetime
from database import (
    supabase,
    get_habits,
    get_profile,
    get_month_snapshots,
)
from calculations import monthly_cost
# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide",
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
    key="reports_home_button",
):
    st.switch_page("app.py")


if "user" not in st.session_state:
    st.session_state.user = get_user()

if st.session_state.user is None:
    st.warning("Please login first.")
    st.stop()

user_email = st.session_state.user.email

if "session" in st.session_state:

    try:

        supabase.auth.set_session(
            st.session_state.session.access_token,
            st.session_state.session.refresh_token,
        )

    except:

        st.stop()
        
#LOAD DATA 

habits = get_habits(user_email)

profile = get_profile(user_email)

snapshots = get_month_snapshots(user_email)

df = pd.DataFrame(habits)

if df.empty:

    st.info("No habits available.")

    st.stop()

df["monthly_cost"] = df.apply(
    lambda row: monthly_cost(
        row["cost"],
        row["frequency"]
    ),
    axis=1
)

#TITLE
# ==========================================
# PAGE HEADER
# ==========================================

st.markdown(
    f'<div class="reports-page-header"><div class="reports-page-eyebrow">📄 FINANCIAL REPORT</div><div class="reports-page-title">Spending &amp; Financial Summary</div><div class="reports-page-subtitle">Review your spending habits, category insights, financial goals, and download professional reports.</div><div class="reports-page-date">Generated on {datetime.now().strftime("%d %B %Y • %I:%M %p")}</div></div>',
    unsafe_allow_html=True,
)

#CALCULATIONS

total_monthly = df["monthly_cost"].sum()

yearly = total_monthly * 12

highest = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .idxmax()
)

highest_amount = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .max()
)

costliest = df.loc[
    df["monthly_cost"].idxmax(),
    "habit"
]

#CARDS

# ==========================================
# SUMMARY CARDS
# ==========================================

summary_cols = st.columns(4)

cards = [
    {
        "icon": "💳",
        "title": "Monthly Spending",
        "value": f"₹ {total_monthly:,.0f}",
        "subtitle": "Current monthly habit cost",
        "class": "report-blue",
    },
    {
        "icon": "📅",
        "title": "Yearly Spending",
        "value": f"₹ {yearly:,.0f}",
        "subtitle": "Projected annual expense",
        "class": "report-purple",
    },
    {
        "icon": "📊",
        "title": "Top Category",
        "value": highest,
        "subtitle": f"₹ {highest_amount:,.0f}/month",
        "class": "report-orange",
    },
    {
        "icon": "🔥",
        "title": "Costliest Habit",
        "value": costliest,
        "subtitle": "Highest monthly expense",
        "class": "report-red",
    },
]

for col, card in zip(summary_cols, cards):
    with col:
        st.markdown(
            f'<div class="report-summary-card {card["class"]}"><div class="report-summary-icon">{card["icon"]}</div><div class="report-summary-title">{card["title"]}</div><div class="report-summary-value">{card["value"]}</div><div class="report-summary-subtitle">{card["subtitle"]}</div></div>',
            unsafe_allow_html=True,
        )
#CATEGORY TABLE 

# ==========================================
# CATEGORY BREAKDOWN
# ==========================================

st.divider()

st.markdown(
    '<div class="section-header"><div class="section-title">📊 Category Breakdown</div><div class="section-subtitle">See how your monthly habit spending is distributed across categories.</div></div>',
    unsafe_allow_html=True,
)

category = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .reset_index()
    .sort_values("monthly_cost", ascending=False)
)

category.columns = [
    "Category",
    "Monthly Cost",
]

max_category_cost = category["Monthly Cost"].max()

category_icons = {
    "Food": "🍔",
    "Shopping": "🛍️",
    "Entertainment": "🎬",
    "Transport": "🚕",
    "Subscriptions": "📱",
    "Health": "💊",
    "Education": "🎓",
    "Travel": "✈️",
    "Other": "📦",
}

category_cols = st.columns(2)

for index, row in category.reset_index(drop=True).iterrows():
    category_name = row["Category"]
    category_cost = row["Monthly Cost"]

    percentage = (
        category_cost / total_monthly * 100
        if total_monthly > 0
        else 0
    )

    progress_width = (
        category_cost / max_category_cost * 100
        if max_category_cost > 0
        else 0
    )

    icon = category_icons.get(category_name, "📦")

    with category_cols[index % 2]:
        st.markdown(
            f'<div class="report-category-card"><div class="report-category-top"><div class="report-category-icon">{icon}</div><div class="report-category-info"><div class="report-category-name">{category_name}</div><div class="report-category-share">{percentage:.1f}% of monthly spending</div></div><div class="report-category-cost">₹ {category_cost:,.0f}</div></div><div class="report-category-progress"><div class="report-category-progress-fill" style="width:{progress_width:.1f}%"></div></div></div>',
            unsafe_allow_html=True,
        )
# ==========================================
# SPENDING HISTORY
# ==========================================

st.divider()

st.markdown(
    '<div class="section-header"><div class="section-title">📈 Spending History</div><div class="section-subtitle">Track how your monthly spending has changed over time.</div></div>',
    unsafe_allow_html=True,
)

if snapshots:
    history_df = pd.DataFrame(snapshots)

    history_df = history_df.sort_values("month")

    latest_spending = history_df.iloc[-1]["spending"]

    if len(history_df) > 1:
        previous_spending = history_df.iloc[-2]["spending"]
        spending_change = latest_spending - previous_spending
        spending_change_percent = (
            spending_change / previous_spending * 100
            if previous_spending > 0
            else 0
        )
    else:
        previous_spending = 0
        spending_change = 0
        spending_change_percent = 0

    history_chart_col, history_info_col = st.columns([2.2, 1])

    with history_chart_col:
        history_fig = px.line(
            history_df,
            x="month",
            y="spending",
            markers=True,
        )

        history_fig.update_traces(
            line=dict(width=4),
            marker=dict(size=9),
            fill="tozeroy",
            hovertemplate="<b>%{x}</b><br>Spending: ₹ %{y:,.0f}<extra></extra>",
        )

        history_fig.update_layout(
            height=370,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            xaxis_title=None,
            yaxis_title=None,
            hovermode="x unified",
            showlegend=False,
        )

        history_fig.update_xaxes(
            showgrid=False,
            color="#94A3B8",
        )

        history_fig.update_yaxes(
            gridcolor="rgba(148,163,184,0.12)",
            tickprefix="₹ ",
            color="#94A3B8",
        )

        st.plotly_chart(
            history_fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with history_info_col:
        st.markdown(
            f'<div class="report-history-latest"><div class="report-history-label">Latest Monthly Spending</div><div class="report-history-value">₹ {latest_spending:,.0f}</div><div class="report-history-note">{history_df.iloc[-1]["month"]}</div></div>',
            unsafe_allow_html=True,
        )

        if spending_change > 0:
            trend_class = "report-history-danger"
            trend_icon = "↗"
            trend_title = "Spending Increased"
            trend_text = (
                f"₹ {abs(spending_change):,.0f} higher than the previous month "
                f"({abs(spending_change_percent):.1f}%)."
            )

        elif spending_change < 0:
            trend_class = "report-history-success"
            trend_icon = "↘"
            trend_title = "Spending Reduced"
            trend_text = (
                f"₹ {abs(spending_change):,.0f} lower than the previous month "
                f"({abs(spending_change_percent):.1f}%)."
            )

        else:
            trend_class = "report-history-neutral"
            trend_icon = "→"
            trend_title = "No Major Change"
            trend_text = "Your spending is unchanged from the previous month."

        st.markdown(
            f'<div class="report-history-trend {trend_class}"><div class="report-history-trend-icon">{trend_icon}</div><div class="report-history-trend-title">{trend_title}</div><div class="report-history-trend-text">{trend_text}</div></div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown(
        '<div class="report-history-empty"><div class="report-history-empty-icon">📭</div><div class="report-history-empty-title">No spending history yet</div><div class="report-history-empty-text">Monthly snapshots will appear here once your spending history is recorded.</div></div>',
        unsafe_allow_html=True,
    )


# ==========================================
# SPENDING DISTRIBUTION
# ==========================================

st.divider()

st.markdown(
    '<div class="section-header"><div class="section-title">🍩 Spending Distribution</div><div class="section-subtitle">Understand which categories take the largest share of your monthly spending.</div></div>',
    unsafe_allow_html=True,
)

distribution_chart_col, distribution_info_col = st.columns([1.7, 1])

with distribution_chart_col:
    fig = px.pie(
        category,
        names="Category",
        values="Monthly Cost",
        hole=0.62,
    )

    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>₹ %{value:,.0f}<br>%{percent}<extra></extra>",
        marker=dict(
            line=dict(
                color="rgba(15,23,42,0.9)",
                width=3,
            )
        ),
    )

    fig.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        showlegend=False,
        annotations=[
            dict(
                text=f"<b>₹ {total_monthly:,.0f}</b><br><span style='font-size:12px'>Monthly Total</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(
                    color="#F8FAFC",
                    size=18,
                ),
            )
        ],
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

with distribution_info_col:
    top_share = (
        highest_amount / total_monthly * 100
        if total_monthly > 0
        else 0
    )

    average_category_cost = (
        category["Monthly Cost"].mean()
        if not category.empty
        else 0
    )

    st.markdown(
        f'<div class="distribution-insight-card"><div class="distribution-insight-icon">📊</div><div class="distribution-insight-label">Largest Spending Share</div><div class="distribution-insight-category">{highest}</div><div class="distribution-insight-value">₹ {highest_amount:,.0f}</div><div class="distribution-insight-note">{top_share:.1f}% of your monthly habit spending</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="distribution-stat-card"><div class="distribution-stat-label">Average Category Cost</div><div class="distribution-stat-value">₹ {average_category_cost:,.0f}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="distribution-stat-card"><div class="distribution-stat-label">Active Categories</div><div class="distribution-stat-value">{len(category)}</div></div>',
        unsafe_allow_html=True,
    )

#PROFILE 

# ==========================================
# FINANCIAL GOAL
# ==========================================

st.divider()

st.markdown(
    '<div class="section-header"><div class="section-title">🎯 Financial Goal</div><div class="section-subtitle">See your current goal, monthly budget, and how your habit spending compares.</div></div>',
    unsafe_allow_html=True,
)

if profile:
    monthly_budget = float(profile.get("monthly_budget") or 0)
    goal = float(profile.get("goal") or 0)
    income = float(profile.get("income") or 0)
    investment_rate = float(profile.get("investment_rate") or 12)
else:
    monthly_budget = 0
    goal = 0
    income = 0
    investment_rate = 12
goal = profile.get("goal", "No goal selected")

budget_used = (
    total_monthly / monthly_budget * 100
    if monthly_budget > 0
    else 0
)

budget_remaining = monthly_budget - total_monthly

goal_col, budget_col = st.columns([1, 1.4])

with goal_col:
    st.markdown(
        f'<div class="report-goal-card"><div class="report-goal-icon">🎯</div><div class="report-goal-label">Current Financial Goal</div><div class="report-goal-title">{goal}</div><div class="report-goal-note">Your report is aligned with this financial objective.</div></div>',
        unsafe_allow_html=True,
    )

with budget_col:
    if monthly_budget > 0:
        progress_width = min(budget_used, 100)

        if budget_used < 80:
            budget_class = "report-budget-success"
            budget_status = "Budget looks healthy"
        elif budget_used <= 100:
            budget_class = "report-budget-warning"
            budget_status = "Approaching budget limit"
        else:
            budget_class = "report-budget-danger"
            budget_status = "Budget exceeded"

        remaining_text = (
            f"₹ {budget_remaining:,.0f} remaining"
            if budget_remaining >= 0
            else f"₹ {abs(budget_remaining):,.0f} over budget"
        )

        st.markdown(
            f'<div class="report-budget-card {budget_class}"><div class="report-budget-header"><div><div class="report-budget-label">Monthly Budget</div><div class="report-budget-value">₹ {monthly_budget:,.0f}</div></div><div class="report-budget-percentage">{budget_used:.1f}%</div></div><div class="report-budget-progress"><div class="report-budget-progress-fill" style="width:{progress_width:.1f}%"></div></div><div class="report-budget-footer"><span>{budget_status}</span><span>{remaining_text}</span></div></div>',
            unsafe_allow_html=True,
        )

    else:
        st.markdown(
            '<div class="report-budget-empty"><div class="report-budget-empty-icon">💰</div><div class="report-budget-empty-title">No monthly budget set</div><div class="report-budget-empty-text">Add a monthly budget in your profile to track spending progress.</div></div>',
            unsafe_allow_html=True,
        )
# ==========================================
# HABIT DETAILS
# ==========================================

st.divider()

st.markdown(
    '<div class="section-header"><div class="section-title">📋 Habit Details</div><div class="section-subtitle">A detailed view of every habit contributing to your monthly expenses.</div></div>',
    unsafe_allow_html=True,
)

habit_icons = {
    "Food": "🍔",
    "Shopping": "🛍️",
    "Entertainment": "🎬",
    "Transport": "🚕",
    "Subscriptions": "📱",
    "Health": "💊",
    "Education": "🎓",
    "Travel": "✈️",
    "Other": "📦",
}

for _, row in df.sort_values("monthly_cost", ascending=False).iterrows():

    icon = habit_icons.get(row["category"], "📦")

    st.markdown(
        f'<div class="report-habit-card"><div class="report-habit-left"><div class="report-habit-icon">{icon}</div><div><div class="report-habit-name">{row["habit"]}</div><div class="report-habit-meta">{row["category"]} • {row["frequency"]}</div></div></div><div class="report-habit-right"><div class="report-habit-cost">₹ {row["monthly_cost"]:,.0f}</div><div class="report-habit-small">₹ {row["cost"]:,.0f} each</div></div></div>',
        unsafe_allow_html=True,
    )
# ==========================================
# REPORT SUMMARY
# ==========================================

st.divider()

st.markdown(
    '<div class="section-header"><div class="section-title">📌 Report Summary</div><div class="section-subtitle">A quick executive overview of your current financial habits.</div></div>',
    unsafe_allow_html=True,
)

summary_items = [
    {
        "icon": "💳",
        "label": "Monthly Spending",
        "value": f"₹ {total_monthly:,.0f}",
    },
    {
        "icon": "📅",
        "label": "Yearly Spending",
        "value": f"₹ {yearly:,.0f}",
    },
    {
        "icon": "📊",
        "label": "Highest Spending Category",
        "value": highest,
    },
    {
        "icon": "🔥",
        "label": "Costliest Habit",
        "value": costliest,
    },
    {
        "icon": "🎯",
        "label": "Financial Goal",
        "value": profile.get("goal", "No goal selected"),
    },
]

summary_rows_html = ""

for item in summary_items:
    summary_rows_html += (
        f'<div class="report-summary-row">'
        f'<div class="report-summary-row-left">'
        f'<div class="report-summary-row-icon">{item["icon"]}</div>'
        f'<div class="report-summary-row-label">{item["label"]}</div>'
        f'</div>'
        f'<div class="report-summary-row-value">{item["value"]}</div>'
        f'</div>'
    )

st.markdown(
    f'<div class="report-executive-card"><div class="report-executive-header"><div class="report-executive-icon">📄</div><div><div class="report-executive-title">Financial Overview</div><div class="report-executive-subtitle">Key figures from your HabitCost report</div></div></div>{summary_rows_html}</div>',
    unsafe_allow_html=True,
)
# ==========================================
# DOWNLOAD REPORTS
# ==========================================

st.divider()

st.markdown(
    '<div class="section-header"><div class="section-title">📥 Download Reports</div><div class="section-subtitle">Export your financial report in CSV or PDF format.</div></div>',
    unsafe_allow_html=True,
)

csv = df.to_csv(index=False)

csv_col, pdf_col = st.columns(2)

# ---------------- CSV ----------------

with csv_col:

    st.markdown(
        '<div class="report-download-card report-download-csv"><div class="report-download-icon">📊</div><div class="report-download-title">CSV Report</div><div class="report-download-text">Download your complete spending dataset for Excel, Google Sheets or further analysis.</div><div class="report-download-meta">Spreadsheet Format</div></div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        "📥 Download CSV Report",
        data=csv,
        file_name=f"HabitCost_Report_{user_email}.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_csv_report",
    )

# ---------------- PDF CARD ----------------

with pdf_col:

    st.markdown(
        '<div class="report-download-card report-download-pdf"><div class="report-download-icon">📄</div><div class="report-download-title">PDF Report</div><div class="report-download-text">Download a professional printable report including spending summary, categories, goals and habits.</div><div class="report-download-meta">Printable Report</div></div>',
        unsafe_allow_html=True,
    )

# ==========================================
# BUILD PDF
# ==========================================

buffer = io.BytesIO()

doc = SimpleDocTemplate(buffer)

styles = getSampleStyleSheet()

story = []

story.append(
    Paragraph(
        "<b>HabitCost Financial Report</b>",
        styles["Title"],
    )
)

story.append(
    Paragraph(
        f"User: {user_email}",
        styles["Normal"],
    )
)

story.append(
    Paragraph(
        f"Monthly Spending: ₹ {total_monthly:,.0f}",
        styles["Normal"],
    )
)

story.append(
    Paragraph(
        f"Yearly Spending: ₹ {yearly:,.0f}",
        styles["Normal"],
    )
)

story.append(
    Paragraph(
        f"Top Category: {highest}",
        styles["Normal"],
    )
)

story.append(
    Paragraph(
        f"Costliest Habit: {costliest}",
        styles["Normal"],
    )
)

story.append(
    Paragraph(
        f"Monthly Budget: ₹ {float(profile.get("monthly_budget") or 0):,.0f}",
        styles["Normal"],
    )
)

story.append(
    Paragraph(
        f"Financial Goal: {profile.get("goal", 0)}",
        styles["Normal"],
    )
)

# Spending History

story.append(
    Paragraph(
        "<br/><b>Spending History</b>",
        styles["Heading2"],
    )
)

if snapshots:

    for row in snapshots:

        story.append(
            Paragraph(
                f"{row['month']} : ₹ {row['spending']:,.0f}",
                styles["Normal"],
            )
        )

# Category Breakdown

story.append(
    Paragraph(
        "<br/><b>Category Breakdown</b>",
        styles["Heading2"],
    )
)

for _, row in category.iterrows():

    story.append(
        Paragraph(
            f"{row['Category']} : ₹ {row['Monthly Cost']:,.0f}",
            styles["Normal"],
        )
    )

# Habit Details

report_df = df[
    [
        "habit",
        "category",
        "cost",
        "frequency",
        "monthly_cost",
    ]
].copy()

report_df.columns = [
    "Habit",
    "Category",
    "Cost",
    "Frequency",
    "Monthly Cost",
]

report_df["Cost"] = report_df["Cost"].map(
    lambda x: f"₹ {x:,.0f}"
)

report_df["Monthly Cost"] = report_df["Monthly Cost"].map(
    lambda x: f"₹ {x:,.0f}"
)

story.append(
    Paragraph(
        "<br/><b>Habit Details</b>",
        styles["Heading2"],
    )
)

for _, row in report_df.iterrows():

    story.append(
        Paragraph(
            f"{row['Habit']} | {row['Category']} | {row['Monthly Cost']}",
            styles["Normal"],
        )
    )

# Notes

story.append(
    Paragraph(
        "<br/><b>Personal Notes</b>",
        styles["Heading2"],
    )
)

notes = profile.get("notes")

if not notes:
    notes = "No notes"

story.append(
    Paragraph(
        notes,
        styles["Normal"],
    )
)

doc.build(story)

buffer.seek(0)

# ==========================================
# PDF DOWNLOAD BUTTON
# ==========================================

with pdf_col:

    st.download_button(
        "📄 Download PDF Report",
        data=buffer,
        file_name=f"HabitCost_Report_{user_email}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_pdf_report",
    )
# ==========================================
# FOOTER
# ==========================================

st.markdown(
    '<div class="reports-footer"><div class="reports-footer-brand">HabitCost Reports</div><div class="reports-footer-tagline">Track • Analyze • Improve • Grow</div><div class="reports-footer-note">This report is automatically generated from your recorded habits and financial profile. Investment projections and summaries are estimates intended for planning purposes only.</div></div>',
    unsafe_allow_html=True,
)