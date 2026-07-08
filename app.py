from insights import generate_insights
import streamlit as st
import pandas as pd

from calculations import *
from charts import spending_pie_chart, category_bar_chart

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(page_title="HabitCost", page_icon="💸", layout="wide")


# ==========================================================
# CUSTOM CSS
# ==========================================================


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()


# ==========================================================
# TITLE
# ==========================================================

st.title("💸 HabitCost")
st.subheader("See where your money and time are really going.")

st.divider()


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("⚙️ User Profile")

currency = st.sidebar.selectbox("Currency", ["₹ INR", "$ USD", "€ EUR", "£ GBP", "AED"])

monthly_income = st.sidebar.number_input(
    "Monthly Income", min_value=0, value=50000, step=1000
)

hours_per_week = st.sidebar.number_input("Hours Worked Per Week", min_value=1, value=40)

investment_rate = st.sidebar.slider("Expected Investment Return (%)", 1, 20, 12)


# ==========================================================
# DASHBOARD
# ==========================================================

st.header("📊 Dashboard")

dashboard_col1, dashboard_col2, dashboard_col3, dashboard_col4 = st.columns(4)

monthly_card = dashboard_col1.empty()
yearly_card = dashboard_col2.empty()
hours_card = dashboard_col3.empty()
future_card = dashboard_col4.empty()

st.divider()


# ==========================================================
# SESSION STATE
# ==========================================================

if "habits" not in st.session_state:
    st.session_state.habits = []


# ==========================================================
# ADD HABIT
# ==========================================================

st.header("➕ Add a New Habit")

habit_name = st.text_input("Habit Name", placeholder="Example: Coffee")

category = st.selectbox(
    "Category",
    [
        "Food",
        "Transport",
        "Entertainment",
        "Shopping",
        "Health",
        "Subscriptions",
        "Education",
        "Other",
    ],
)

cost = st.number_input("Cost", min_value=0.0, value=250.0, step=10.0)

frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "Yearly"])

if st.button("➕ Add Habit"):

    if habit_name.strip() == "":
        st.warning("Please enter a habit name.")

    else:

        st.session_state.habits.append(
            {
                "Habit": habit_name,
                "Category": category,
                "Cost": cost,
                "Frequency": frequency,
            }
        )

        st.success("Habit added successfully!")

# ==========================================================
# HABIT TABLE
# ==========================================================

st.divider()

st.header("📋 Your Habits")

if len(st.session_state.habits) == 0:

    st.info("No habits added yet.")

else:

    # ------------------------------------------------------
    # CREATE DATAFRAME
    # ------------------------------------------------------

    df = pd.DataFrame(st.session_state.habits)

    df["Monthly Cost"] = df.apply(
        lambda row: monthly_cost(row["Cost"], row["Frequency"]), axis=1
    )

    df["Yearly Cost"] = df["Monthly Cost"] * 12

    df["20 Year Cost"] = df["Yearly Cost"] * 20

    # ------------------------------------------------------
    # BIGGEST MONEY LEAK
    # ------------------------------------------------------

    largest_habit = df.loc[df["Monthly Cost"].idxmax()]
    percentage = (largest_habit["Monthly Cost"] / df["Monthly Cost"].sum()) * 100

    st.divider()

    st.header("⚠️ Biggest Money Leak")

    leak_col1, leak_col2 = st.columns([1, 2])

    with leak_col1:

        st.metric(
            "Monthly Cost",
            f"{currency.split()[0]} {largest_habit['Monthly Cost']:,.0f}",
        )

    with leak_col2:

        st.subheader(f"💸 {largest_habit['Habit']}")

        st.write(
            f"**Yearly Cost:** "
            f"{currency.split()[0]} "
            f"{largest_habit['Yearly Cost']:,.0f}"
        )

        st.write(
            f"This habit accounts for "
            f"**{percentage:.1f}%** "
            f"of your monthly spending."
        )

    # ------------------------------------------------------
    # ACTIVE HABITS
    # ------------------------------------------------------
    st.divider()

    st.header("📋 Active Habits")

    habit_icons = {
        "Food": "🍔",
        "Transport": "🚗",
        "Entertainment": "🎬",
        "Shopping": "🛍️",
        "Health": "💪",
        "Subscriptions": "📺",
        "Education": "📚",
        "Other": "💸",
    }

    for index, habit in enumerate(st.session_state.habits):

        monthly = monthly_cost(habit["Cost"], habit["Frequency"])

        yearly = monthly * 12

        icon = habit_icons.get(habit["Category"], "💸")

        left, middle, right = st.columns([5, 2, 1])

        with left:

            st.markdown(f"### {icon} {habit['Habit'].title()}")

            st.caption(f"{habit['Category']} • {habit['Frequency']}")

            st.write(f"**Yearly Cost:** {currency.split()[0]} {yearly:,.0f}")

        with middle:

            st.metric("Monthly Cost", f"{currency.split()[0]} {monthly:,.0f}")

        with right:

            if st.button("🗑️", key=f"delete_{index}"):

                st.session_state.habits.pop(index)

                st.rerun()

        st.divider()
    # ------------------------------------------------------
    # DETAILED BREAKDOWN
    # ------------------------------------------------------

    st.divider()

    st.header("📊 Detailed Breakdown")

    st.dataframe(
        df[["Habit", "Category", "Monthly Cost", "Yearly Cost", "20 Year Cost"]],
        use_container_width=True,
        hide_index=True,
    )

    # ======================================================
    # DASHBOARD CALCULATIONS
    # ======================================================

    total_monthly = df["Monthly Cost"].sum()

    total_yearly = df["Yearly Cost"].sum()

    weekly_income = monthly_income / 4

    hourly_income = weekly_income / hours_per_week

    if hourly_income > 0:
        hours_worked = total_monthly / hourly_income
    else:
        hours_worked = 0

    future_20 = future_value(total_monthly, investment_rate, 20)
    # ======================================================
    # UPDATE DASHBOARD
    # ======================================================

    monthly_card.metric(
        "💰 Monthly Spending", f"{currency.split()[0]} {total_monthly:,.2f}"
    )

    yearly_card.metric(
        "📅 Yearly Spending", f"{currency.split()[0]} {total_yearly:,.2f}"
    )

    hours_card.metric("⏳ Hours Worked", f"{hours_worked:.1f} hrs")

    future_card.metric(
        "📈 Future Value (20 Years)", f"{currency.split()[0]} {future_20:,.0f}"
    )

    # ======================================================
    # FUTURE VALUE PROJECTION
    # ======================================================

    st.divider()

    st.header("📈 Future Value Projection")

    years = [5, 10, 20, 30]

    projection_cols = st.columns(4)

    for i, year in enumerate(years):

        value = future_value(total_monthly, investment_rate, year)

        projection_cols[i].metric(
            f"{year} Years", f"{currency.split()[0]} {value:,.0f}"
        )

    # ======================================================
    # SPENDING BREAKDOWN
    # ======================================================

    st.divider()

    st.header("🥧 Spending Breakdown")

    fig = spending_pie_chart(df)

    st.plotly_chart(fig, use_container_width=True, key="spending_breakdown_chart")
    st.divider()
    st.header("📊 Spending by Category")
    category_fig = category_bar_chart(df)
    st.plotly_chart(category_fig, use_container_width=True, key="category_chart")
    st.divider()

    st.header("💡 Smart Insights")

    insights = generate_insights(df, future_20)

    st.warning(insights[0])
    st.error(insights[1])
    st.info(insights[2])
    st.success(insights[3])
