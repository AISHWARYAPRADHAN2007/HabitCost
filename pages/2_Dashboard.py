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
if st.button("🏠 Home"):
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

st.title("📊 Financial Dashboard")

st.caption(
    "Understand where your money goes and how habits impact your future."
)


st.divider()


# ==========================================
# TOP SUMMARY CARDS
# ==========================================

st.markdown(
    """
    <style>

    .card {

        padding:20px;
        border-radius:18px;
        border:1px solid #ddd;
        text-align:center;
        margin-bottom:10px;

    }

    .card-title {

        font-size:18px;
        color:#666;

    }

    .card-value {

        font-size:30px;
        font-weight:700;

    }

    </style>
    """,
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="card">

        <div class="card-title">
        💸 Monthly Spending
        </div>

        <div class="card-value">
        ₹ {total_monthly_spending:,.0f}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="card">

        <div class="card-title">
        📌 Habits Tracked
        </div>

        <div class="card-value">
        {total_habits}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="card">

        <div class="card-title">
        🔥 Biggest Category
        </div>

        <div class="card-value">
        {top_category}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="card">

        <div class="card-title">
        💰 Category Cost
        </div>

        <div class="card-value">
        ₹ {top_category_amount:,.0f}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# MONTHLY SNAPSHOT
# ==========================================
# ==========================================
# MONTHLY SNAPSHOT
# ==========================================

st.subheader("📅 Monthly Snapshot")

with st.container():

    if "snapshot_saved" not in st.session_state:
        st.session_state.snapshot_saved = False


    if st.session_state.snapshot_saved:
        st.success("✅ Monthly snapshot saved successfully!")
        st.session_state.snapshot_saved = False


    if st.button(
        "💾 Save Monthly Snapshot",
        use_container_width=True
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

st.subheader("🧠 Financial Health Score")

subscription_cost = (
    df[
        df["category"] == "Subscriptions"
    ]["monthly_cost"]
    .sum()
)

score = 100


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

col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Financial Health Score",
        f"{score}/100"
    )


with col2:

    if score >= 80:
        message = "🟢 Excellent financial habits"

    elif score >= 60:
        message = "🟡 Good, but can improve"

    else:
        message = "🔴 Needs attention"


    st.write(message)
# ==========================================
# MONTHLY BUDGET TRACKER
# ==========================================

st.divider()

st.subheader(
    "📅 Monthly Budget Tracker"
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
        profile["income"],
        profile["currency"],
        profile["investment_rate"],
        new_budget,
        profile["goal"],
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


    col1, col2, col3 = st.columns(3)


    with col1:
        st.metric(
            "Budget",
            f"₹ {new_budget:,.0f}"
        )

    with col2:
        st.metric(
            "Spent",
            f"₹ {spent:,.0f}"
        )


    with col3:
        st.metric(
            "Remaining",
            f"₹ {remaining:,.0f}"
        )


    st.progress(
        min(progress,1)
    )

# ==========================================
# ACHIEVEMENTS
# ==========================================

st.divider()

st.subheader(
    "🏆 Achievements"
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
                <div style="
                    padding:20px;
                    border-radius:20px;
                    border:2px solid #4CAF50;
                    text-align:center;
                    margin-bottom:20px;
                ">

                <h1>
                🏆
                </h1>

                <h3>
                {badge['title']}
                </h3>

                <p>
                {badge['description']}
                </p>

                <b>
                UNLOCKED ✅
                </b>

                </div>
                """,
                unsafe_allow_html=True
            )


        else:

            st.markdown(
                f"""
                <div style="
                    padding:20px;
                    border-radius:20px;
                    border:2px solid #cccccc;
                    text-align:center;
                    margin-bottom:20px;
                ">

                <h1>
                🔒
                </h1>

                <h3>
                {badge['title']}
                </h3>

                <p>
                {badge['description']}
                </p>

                <b>
                LOCKED
                </b>

                </div>
                """,
                unsafe_allow_html=True
            )


    index += 1
# ==========================================
# PERSONALIZED RECOMMENDATIONS
# ==========================================

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

        st.markdown(
            f"""
            <div style="
                padding:18px;
                border-radius:18px;
                border-left:8px solid orange;
                background-color:#262626;
                color:white;
                border-left:8px solid #f5a623;
                margin-bottom:15px;
            ">

            <h3 style="color:white;">
            💡 Money Saving Tip
            </h3>

            <p style="color:#dddddd;">
            {rec['message']}
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    elif rec["type"] == "success":

        st.markdown(
            f"""
            <div style="
                padding:18px;
                border-radius:18px;
                border-left:8px solid green;
                background-color:#262626;
                color:white;
                border-left:8px solid #4CAF50;
                margin-bottom:15px;
            ">

            <h3 style="color:white;">
            🎯 Smart Move
            </h3>

            <p style="color:#dddddd;">
            {rec['message']}
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    elif rec["type"] == "danger":

        st.markdown(
            f"""
            <div style="
                padding:18px;
                border-radius:18px;
                border-left:8px solid red;
                background-color:#262626;
                color:white;
                border-left:8px solid #ff4b4b;
                margin-bottom:15px;
            ">

            <h3 style="color:white;">
            🚨 Attention Needed
            </h3>

            <p style="color:#dddddd;">
            {rec['message']}
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    else:

        st.info(
            rec["message"]
        )
# ==========================================
# ANALYTICS PREVIEW
# ==========================================

st.divider()

st.subheader("📈 Analytics Preview")

preview_col1, preview_col2 = st.columns([2, 1])

with preview_col1:

    category_preview = (
        df.groupby("category")["monthly_cost"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_preview)

with preview_col2:

    st.metric(
        "Top Category",
        top_category
    )

    st.metric(
        "Monthly Cost",
        f"₹ {top_category_amount:,.0f}"
    )

    st.info(
        "See detailed spending insights in the 📈 Analytics page."
    )
    
# ==========================================
# SPENDING VISUALIZATION
# ==========================================

st.divider()

st.subheader("📊 Spending Visualization")

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
        color="Category",
        text_auto=True,
        title="Monthly Spending by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col2:

    fig = px.pie(
        category_chart,
        names="Category",
        values="Monthly Cost",
        hole=0.5,
        title="Spending Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ==========================================
# TOP SAVINGS OPPORTUNITIES
# ==========================================

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

st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True
)

highest = top_habits.iloc[0]

st.success(
    f"""
💰 If you reduce **{highest['habit']}** by just **50%**, you could save approximately **₹ {highest['monthly_cost']/2:,.0f} every month**.

See the **💹 Investments** page to estimate how much this could grow over time.
"""
)

st.divider()

