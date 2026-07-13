import streamlit as st
import pandas as pd

from database import supabase
from auth import signup, login, get_user, logout, reset_password
from database import get_habits

from calculations import monthly_cost


st.set_page_config(
    page_title="HabitCost",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# ==========================================================
# CUSTOM CSS
# ==========================================================


def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# ==========================================================
# AUTHENTICATION
# ==========================================================

if "user" not in st.session_state:
    st.session_state.user = get_user()

if "session" in st.session_state and st.session_state.session:

    supabase.auth.set_session(
        st.session_state.session.access_token,
        st.session_state.session.refresh_token
    )

if st.session_state.user is None:

    st.markdown("""
    <div style="text-align:center; margin-top:30px; margin-bottom:20px;">
        <div style="font-size:70px;">💸</div>
        <h1 style="margin-bottom:5px;">HabitCost</h1>
        <p style="font-size:18px;color:gray;">
            Track habits. Understand spending. Build wealth.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align:center;'>Get Started</h2>",
        unsafe_allow_html=True,
    )

    left, centre, right = st.columns([1.5, 2, 1.5])

    with centre:

        choice = st.selectbox(
            "Choose an option",
            ["Login", "Sign Up"]
        )

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

    # -----------------------------
    # SIGN UP
    # -----------------------------
    if choice == "Sign Up":

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:

            signup_clicked = st.button(
                "Create Account",
                key="signup_button",
                use_container_width=True
            )

        if signup_clicked:

            response = signup(email, password)

            if response:
                st.success(
                    "✅ Account created! Check your email to verify your account."
                )

    # -----------------------------
    # LOGIN
    # -----------------------------
    else:

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:

            login_clicked = st.button(
                "Login",
                key="login_button",
                use_container_width=True
            )

        if login_clicked:

            response = login(email, password)

            if response and response.user:

                st.session_state.user = response.user
                st.session_state.session = response.session

                supabase.auth.set_session(
                    response.session.access_token,
                    response.session.refresh_token
                )

                st.rerun()

            else:

                st.error("❌ Invalid email or password.")
    st.markdown("---")

    if st.button("🔑 Forgot Password?"):

      st.session_state.show_reset = True
    if st.session_state.get("show_reset"):

      st.subheader("Reset Password")

      reset_email = st.text_input(
        "Enter your email",
        key="reset_email"
    )

    if st.button("Send Reset Link"):

        success, msg = reset_password(email)

        if success:
            st.success(msg)
        else:
            st.error(msg)

    st.stop()

# ==========================================================
# SIDEBAR
# ==========================================================

import streamlit as st


# after login check

username = (
    st.session_state.user.email
    .split("@")[0]
    .replace(".", " ")
    .replace("_", " ")
    .title()
    if st.session_state.user and st.session_state.user.email
    else "User"
)

from datetime import datetime


hour = datetime.now().hour

if hour < 12:
    greeting = "Good Morning ☀️"
elif hour < 17:
    greeting = "Good Afternoon 🌤️"
else:
    greeting = "Good Evening 🌙"

st.markdown(
    f"""
    <div style="padding:5px 0 25px 0;">
        <h1>{greeting}, {username} 👋</h1>
        <p style="font-size:18px; color:#9CA3AF;">
            Small habits create big wealth.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
top1, top2 = st.columns([8, 1])

with top2:

    with st.popover("⚙️ Account"):

        if st.button(
            "⚙️ Settings",
            use_container_width=True,
        ):
            st.switch_page("pages/6_Settings.py")

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
        ):
            logout()

            st.session_state.user = None
            st.session_state.session = None

            st.rerun()
# ==========================================================
# HOME SUMMARY
# ==========================================================

from database import get_habits, get_profile
from calculations import monthly_cost, future_value


user_email = st.session_state.user.email

habits = get_habits(user_email)
home_df = pd.DataFrame(habits)
# ==========================================
# HOME FINANCIAL CALCULATIONS
# ==========================================

if not home_df.empty:

    home_df["Monthly Cost"] = home_df.apply(
        lambda row: monthly_cost(
            row["cost"],
            row["frequency"]
        ),
        axis=1
    )

    total_monthly_spending = home_df["Monthly Cost"].sum()

    total_habits = len(home_df)

else:

    total_monthly_spending = 0

    total_habits = 0
home_df = home_df.rename(
    columns={
        "habit": "Habit",
        "category": "Category"
    }
)

if not home_df.empty:
    home_df["Yearly Cost"] = home_df["Monthly Cost"] * 12


else:

    home_df = pd.DataFrame(
        columns=[
            "Habit",
            "Category",
            "Cost",
            "Frequency",
            "Monthly Cost",
            "Yearly Cost"
        ]
    )

profile = get_profile(user_email)

monthly_budget = 0

if profile:
    monthly_budget = profile.get("monthly_budget", 0)

    if monthly_budget is None:
        monthly_budget = 0
        
monthly_budget = 0

if profile:
    monthly_budget = profile.get("monthly_budget", 0)

    if monthly_budget is None:
        monthly_budget = 0

currency = "₹"

if profile:
    currency = profile.get("currency", "₹ INR").split()[0]
    investment_rate = profile.get("investment_rate", 12)
else:
    investment_rate = 12


total_monthly = 0

for habit in habits:
    total_monthly += monthly_cost(
        habit["cost"],
        habit["frequency"]
    )


future = future_value(
    total_monthly,
    investment_rate,
    20
)

# ==========================================
# FINANCIAL HEALTH SCORE CALCULATION
# ==========================================

if not home_df.empty:

    subscription_cost = (
        home_df[
            home_df["Category"] == "Subscriptions"
        ]["Monthly Cost"]
        .sum()
    )

else:
    subscription_cost = 0


score = 100


# Budget overspending penalty
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

st.markdown("## 📊 Financial Overview")
card1, card2, card3, card4 = st.columns(4)


with card1:
    st.metric(
        "💰 Monthly Spending",
        f"{currency} {total_monthly:,.0f}"
    )


with card2:
    st.metric(
        "🔥 Active Habits",
        len(habits)
    )


with card3:
    st.metric(
        "📈 20 Year Potential",
        f"{currency} {future:,.0f}"
    )
with card4:
    st.metric(
        "🏆 Financial Score",
        f"{score}/100"
    )

st.divider()


st.subheader("YOUR WORKSPACE")
st.caption("Everything you need to track, analyze, and improve your spending.")

st.write("")


col1, col2, col3 = st.columns(3)


with col1:

    if st.button(
        "🔥\n\nHABITS\n\nManage Habits",
        use_container_width=True,
        key="home_habits"
    ):
        st.switch_page("pages/1_Habits.py")
        
    if st.button(
        "💹\n\nINVESTMENT\n\nFuture growth",
        use_container_width=True,
        key="home_investments"
    ):
        st.switch_page("pages/4_Investments.py")
    


with col2:
    
    if st.button(
        "📊\n\nDASHBOARD\n\nInsights & Statistics",
        use_container_width=True,
        key="home_dashboard"
    ):
        st.switch_page("pages/2_Dashboard.py")
    
    if st.button(
        "📄\n\nREPORTS\n\nDownload Reports",
        use_container_width=True,
        key="home_reports"
    ):
        st.switch_page("pages/5_Reports.py")




with col3:
    
    if st.button(
        "📈\n\nANALYTICS\n\nAnalyze your spending",
        use_container_width=True,
        key="home_analytics"
    ):
        st.switch_page("pages/3_Analytics.py")


    if st.button(
        "⚙️\n\nSETTINGS\n\nProfile",
        use_container_width=True,
        key="home_settings"
    ):
        st.switch_page("pages/6_Settings.py")



# ==========================================================
# HOME SPENDING OVERVIEW
# ==========================================================

st.subheader("🥧 Spending Overview")


if len(home_df) > 0:

    category_spending = (
        home_df
        .groupby("Category")["Monthly Cost"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    spend_col1, spend_col2 = st.columns([2, 1])


    with spend_col1:

        for category, amount in category_spending.items():

            st.write(
                f"**{category}**"
            )

            st.progress(
                float(
                    amount /
                    category_spending.max()
                )
            )

            st.caption(
                f"{currency} {amount:,.0f}/month"
            )


    with spend_col2:

        top_category = category_spending.idxmax()

        st.metric(
            "🏆 Highest Spending Category",
            top_category
        )

        st.metric(
            "💸 Amount",
            f"{currency} {category_spending.max():,.0f}"
        )


else:

    st.info(
        "Add habits to view your spending breakdown."
    )


st.divider()



st.caption(
    "HabitCost • Version 1.0 • Built with ❤️"
)