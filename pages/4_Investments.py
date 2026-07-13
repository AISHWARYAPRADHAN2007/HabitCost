import streamlit as st
import pandas as pd
from auth import logout
from auth import get_user

from database import (
    supabase,
    get_habits,
    get_profile,
)
from calculations import monthly_cost

if st.button("🏠 Home"):
    st.switch_page("app.py")


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Investments",
    page_icon="💹",
    layout="wide"
)


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
            st.session_state.session.refresh_token
        )

    except:

        st.warning("Session expired.")
        st.stop()


# ==========================================
# LOAD HABITS
# ==========================================

habits = get_habits(user_email)

df = pd.DataFrame(habits)

if df.empty:

    st.info("No habits added yet.")

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

st.title("💹 Investments")

st.caption(
    "See how reducing small habits today can build wealth tomorrow."
)

st.divider()

# ==========================================
# SAVINGS SIMULATOR
# ==========================================

st.divider()

st.subheader(
    "💰 Savings Simulator"
)


habit_options = df["habit"].tolist()


selected_habit = st.selectbox(
    "Choose a habit to reduce",
    habit_options
)


selected_data = df[
    df["habit"] == selected_habit
].iloc[0]


reduction = st.slider(
    "Reduce habit by (%)",
    min_value=10,
    max_value=100,
    value=50,
    step=10
)


monthly_saving = (
    selected_data["monthly_cost"]
    *
    reduction
    /
    100
)


yearly_saving = monthly_saving * 12


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Monthly Saving",
        f"₹ {monthly_saving:,.0f}"
    )


with col2:

    st.metric(
        "Yearly Saving",
        f"₹ {yearly_saving:,.0f}"
    )
daily_saving = monthly_saving / 30

st.metric(
    "☕ Daily Saving",
    f"₹ {daily_saving:,.0f}"
)
st.divider()
# ==========================================
# FUTURE VALUE PREDICTION
# ==========================================

st.divider()

st.subheader(
    "🔮 Future Value Prediction"
)


monthly_saving = monthly_saving


years = st.slider(
    "Investment Duration (Years)",
    min_value=1,
    max_value=30,
    value=5
)


rate = st.slider(
    "Expected Annual Return (%)",
    min_value=1,
    max_value=20,
    value=8
)


monthly_rate = rate / 12 / 100

months = years * 12


future_value = (
    monthly_saving
    *
    (
        ((1 + monthly_rate) ** months - 1)
        /
        monthly_rate
    )
)


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Monthly Investment",
        f"₹ {monthly_saving:,.0f}"
    )


with col2:

    st.metric(
        "Future Value",
        f"₹ {future_value:,.0f}"
    )
amount_invested = monthly_saving * months

interest_earned = future_value - amount_invested

st.write("")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "💰 Total Invested",
        f"₹ {amount_invested:,.0f}"
    )

with col2:

    st.metric(
        "📈 Interest Earned",
        f"₹ {interest_earned:,.0f}"
    )
# ==========================================
# INVESTMENT GROWTH CHART
# ==========================================

st.divider()

st.subheader("📈 Investment Growth")


growth = []

balance = 0


for year in range(1, years + 1):

    months_elapsed = year * 12

    value = (
        monthly_saving
        *
        (
            ((1 + monthly_rate) ** months_elapsed - 1)
            /
            monthly_rate
        )
    )

    growth.append(
        {
            "Year": year,
            "Value": value
        }
    )


growth_df = pd.DataFrame(growth)

st.line_chart(
    growth_df.set_index("Year")
)

# ==========================================
# SCENARIO COMPARISON
# ==========================================

st.divider()

st.subheader("📊 Investment Scenarios")


comparison = []


for y in [5, 10, 15, 20]:

    months = y * 12

    value = (
        monthly_saving
        *
        (
            ((1 + monthly_rate) ** months - 1)
            /
            monthly_rate
        )
    )

    comparison.append(
        {
            "Years": y,
            "Future Value": f"₹ {value:,.0f}"
        }
    )


comparison_df = pd.DataFrame(
    comparison
)

st.dataframe(
    comparison_df,
    hide_index=True,
    use_container_width=True
)

# ==========================================
# INVESTMENT INSIGHT
# ==========================================

st.divider()

st.subheader("💡 Investment Insight")


st.success(

    f"""
Reducing **{selected_habit}** by **{reduction}%**

saves you **₹ {monthly_saving:,.0f} every month**.

If you invest that amount for **{years} years**
at **{rate}% annual return**,

it could grow to

# 💰 ₹ {future_value:,.0f}
"""
)
profile = get_profile(user_email)
if profile:

    st.success(
        f"""
Your current goal is **{profile['goal']}**.

Keep investing consistently to get closer to achieving it!
"""
    )
# ==========================================
# WHAT COULD THIS BECOME?
# ==========================================

st.divider()

st.subheader("🎯 What Could This Become?")


ideas = []


if future_value >= 20000:
    ideas.append("⌚ A premium smartwatch")

if future_value >= 50000:
    ideas.append("📱 A flagship smartphone")

if future_value >= 100000:
    ideas.append("💻 A high-end laptop")

if future_value >= 150000:
    ideas.append("🎓 Pay for a professional certification or online courses")

if future_value >= 200000:
    ideas.append("🏍️ A bike down payment")

if future_value >= 300000:
    ideas.append("🌍 A dream international vacation")

if future_value >= 500000:
    ideas.append("🚗 A car down payment")

if future_value >= 700000:
    ideas.append("💍 A wedding fund")

if future_value >= 1000000:
    ideas.append("🏠 A house down payment")

if future_value >= 1500000:
    ideas.append("🚀 Seed money to start your own business")

if future_value >= 2500000:
    ideas.append("🎓 Help fund a university degree")

if future_value >= 5000000:
    ideas.append("💼 Build a serious long-term investment portfolio")


if ideas:

    st.success(
        "Instead of spending on this habit, your money could become:"
    )

    for item in ideas:

        st.write(item)

else:

    st.info(
        "Every investment starts small. Keep investing consistently!"
    )
profile = get_profile(user_email)

if profile:

    goal = profile["goal"]

    st.divider()

    st.subheader("🎯 Goal Progress")

    st.success(
        f"Current Goal: **{goal}**"
    )

    if goal == "Save More":

        st.info(
            "💰 Continue investing consistently to grow your savings."
        )

    elif goal == "Reduce Spending":

        st.info(
            "📉 Every unnecessary habit you reduce moves you closer to this goal."
        )

    elif goal == "Build Emergency Fund":

        st.info(
            "🛟 Build at least 6 months of expenses for financial security."
        )

    elif goal == "Travel":

        st.info(
            "✈️ Your investments can become your next vacation fund."
        )

    elif goal == "Buy a Laptop":

        st.info(
            "💻 Keep investing until you can buy your laptop without debt."
        )

    elif goal == "Buy a Vehicle":

        st.info(
            "🏍️ Your monthly investments can become a vehicle down payment."
        )

    elif goal == "Buy a House":

        st.info(
            "🏠 Long-term investing is a great way to build a home down payment."
        )

    elif goal == "Invest More":

        st.info(
            "📈 Increase your SIP whenever your income increases."
        )

    elif goal == "Education":

        st.info(
            "🎓 Your investments can fund future studies and certifications."
        )

    else:

        st.info(
            "🌟 Stay consistent. Every investment brings you closer to your goal."
        )
st.divider()

st.subheader("📚 Investment Tips")

tips = [
    "💡 Invest every month, even if it's a small amount.",
    "📈 The earlier you start, the more compounding works for you.",
    "💰 Increase investments whenever your salary increases.",
    "🚫 Avoid withdrawing investments unless absolutely necessary.",
    "🎯 Stay consistent rather than trying to time the market."
]

for tip in tips:

    st.info(tip)
st.divider()

