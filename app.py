import streamlit as st
import pandas as pd

from datetime import datetime

from database import (
    supabase,
    get_habits,
    get_profile,
)

from auth import (
    signup,
    login,
    get_user,
    logout,
    reset_password,
)

from calculations import (
    monthly_cost,
    future_value,
)


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
    try:
        with open("assets/style.css", encoding="utf-8") as css_file:
            st.markdown(
                f"<style>{css_file.read()}</style>",
                unsafe_allow_html=True,
            )
    except FileNotFoundError:
        st.warning("Could not find assets/style.css")


load_css()

if "user" not in st.session_state:
    st.session_state.user = get_user()

if "reset_mode" not in st.session_state:
    st.session_state.reset_mode = False

if "show_reset" not in st.session_state:
    st.session_state.show_reset = False
# ==========================================================
# AUTHENTICATION
# ==========================================================

if (
    "session" in st.session_state
    and st.session_state.session
):
    try:
        supabase.auth.set_session(
            st.session_state.session.access_token,
            st.session_state.session.refresh_token,
        )

    except Exception:
        st.session_state.user = None
        st.session_state.session = None

# Check whether the recovery URL contains type=recovery
if (
    "type" in st.query_params
    and st.query_params["type"] == "recovery"
):
    st.session_state.reset_mode = True


if st.session_state.user is None:

    left, middle, right = st.columns(
        [1.25, 0.08, 0.9]
    )

    # ======================================================
    # LEFT PANEL
    # ======================================================

    with left:

        st.markdown(
            """
<div style="padding-top:40px;">

<div class="hero-title">
💸 HabitCost
</div>

<div class="hero-subtitle">
Track habits.<br>
Understand spending.<br>
Build wealth.
</div>

</div>
""",
            unsafe_allow_html=True,
        )

        st.write("")

        features = [
            
            (
                "💸",
                "Track Daily Spending",
                "Monitor every expense effortlessly.",
            ),
            (
                "📊",
                "Powerful Analytics",
                "Discover trends and spending patterns.",
            ),
            (
                "📈",
                "Future Value Calculator",
                "See how today's habits affect tomorrow.",
            ),
            (
                "🧠",
                "Personalized Insights",
                "Get smart recommendations based on your habits.",
            ),
        ]

        for icon, title, description in features:
            left_space, card, right_space = st.columns([0.02, 0.93, 0.05])

            with card:
                
                st.markdown(
                    f"""
                    <div class="feature-card">
                       <div class="feature-icon">{icon}</div>

                       <div>
                           <div class="feature-title">{title}</div>
                           <div class="feature-description">
                               {description}
                           </div>
                       </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    # The middle column is intentionally empty.
    # It creates spacing between both panels.

    # ======================================================
    # RIGHT PANEL
    # ======================================================

    with right:
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        auth_card = st.container(border=True)

        with auth_card:

            st.markdown("### Welcome Back 👋")
            st.caption("Sign in to continue to HabitCost")
            st.write("")

            choice = st.radio(
                "Account action",
                ["Login", "Sign Up"],
                horizontal=True,
                label_visibility="collapsed",
            )

            email = st.text_input(
                "📧 Email",
                placeholder="Enter your email",
                key="auth_email",
            )

            password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                key="auth_password",
            )

            # ----------------------------------------------
            # RESET PASSWORD MODE
            # ----------------------------------------------

            if st.session_state.get("reset_mode"):

                st.subheader("🔐 Set New Password")

                new_password = st.text_input(
                    "New Password",
                    type="password",
                    key="new_password",
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    key="confirm_password",
                )

                if st.button(
                    "Update Password",
                    key="update_password_button",
                    use_container_width=True,
                ):

                    if not new_password or not confirm_password:
                        st.error("Please fill in both password fields.")

                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")

                    elif len(new_password) < 6:
                        st.error(
                            "Password must be at least 6 characters."
                        )

                    else:

                        try:

                            supabase.auth.update_user(
                                {"password": new_password}
                            )

                            st.success(
                                "Password updated successfully. Please log in."
                            )

                            st.session_state.reset_mode = False
                            st.query_params.clear()
                            st.rerun()

                        except Exception as e:
                            st.error(str(e))

                st.stop()

            # ----------------------------------------------
            # SIGN UP
            # ----------------------------------------------

            if choice == "Sign Up":

                if st.button(
                    "✨ Create Account",
                    key="signup_button",
                    use_container_width=True,
                ):

                    clean_email = email.strip()

                    if not clean_email or not password:
                        st.error(
                            "Please enter your email and password."
                        )

                    elif len(password) < 6:
                        st.error(
                            "Password must be at least 6 characters."
                        )

                    else:

                        response = signup(
                            clean_email,
                            password,
                        )

                        if response:
                            st.success(
                                "✅ Account created! Check your email "
                                "to verify your account."
                            )

            # ----------------------------------------------
            # LOGIN
            # ----------------------------------------------

            else:

                if st.button(
                    "🚀 Login",
                    key="login_button",
                    use_container_width=True,
                ):

                    clean_email = email.strip()

                    if not clean_email or not password:
                        st.error(
                            "Please enter your email and password."
                        )

                    else:

                        response = login(
                            clean_email,
                            password,
                        )

                        if response and response.user:

                            st.session_state.user = response.user
                            st.session_state.session = response.session

                            supabase.auth.set_session(
                                response.session.access_token,
                                response.session.refresh_token,
                            )

                            st.rerun()

                        else:
                            st.error(
                                "❌ Invalid email or password."
                            )

                if st.button(
                    "🔑 Forgot Password?",
                    key="forgot_button",
                    use_container_width=True,
                ):

                    st.session_state.show_reset = (
                        not st.session_state.get(
                            "show_reset",
                            False,
                        )
                    )

                if st.session_state.get("show_reset"):

                    reset_email = st.text_input(
                        "Recovery email",
                        placeholder="Enter your registered email",
                        key="reset_email",
                    )

                    if st.button(
                        "Send Reset Link",
                        key="reset_button",
                        use_container_width=True,
                    ):

                        clean_reset_email = reset_email.strip()

                        if not clean_reset_email:
                            st.error("Please enter your email.")

                        else:

                            success, msg = reset_password(
                                clean_reset_email
                            )

                            if success:
                                st.success(msg)
                            else:
                                st.error(msg)

    st.stop()
    
# ==========================================================
# SIDEBAR
# ==========================================================




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




hour = datetime.now().hour

if hour < 12:
    greeting = "Good Morning ☀️"
elif hour < 17:
    greeting = "Good Afternoon 🌤️"
else:
    greeting = "Good Evening 🌙"

top1, top2 = st.columns([8, 1.4])

with top1:
    st.markdown(
        f'<div class="home-welcome-header"><div class="home-welcome-title">{greeting}, {username} 👋</div><div class="home-welcome-subtitle">Small habits create big wealth.</div></div>',
        unsafe_allow_html=True,
    )

with top2:
    with st.popover(
        "⚙️ Account",
        use_container_width=True,
    ):
        if st.button(
            "⚙️ Settings",
            use_container_width=True,
            key="account_settings_button",
        ):
            st.switch_page("pages/6_Settings.py")

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="account_logout_button",
        ):
            logout()

            st.session_state.user = None
            st.session_state.session = None

            st.rerun()
# ==========================================================
# HOME SUMMARY
# ==========================================================




user_email = st.session_state.user.email

try:
    habits = get_habits(user_email) or []

except Exception as error:
    st.error(
        f"Unable to load your habits: {error}"
    )
    habits = []

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

try:
    profile = get_profile(user_email)

except Exception as error:
    st.error(
        f"Unable to load your profile: {error}"
    )
    profile = None

monthly_budget = 0

if profile:
    monthly_budget = profile.get("monthly_budget", 0)

    if monthly_budget is None:
        monthly_budget = 0

currency_codes = {
    "INR": "₹",
    "AED": "د.إ",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
}

if profile:
    profile_currency = profile.get("currency") or "INR"
    investment_rate = float(
        profile.get("investment_rate") or 12
    )
else:
    profile_currency = "INR"
    investment_rate = 12

currency = currency_codes.get(
    profile_currency,
    profile_currency,
)

total_monthly = total_monthly_spending


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


score = max(
    0,
    min(score, 100),
)

st.markdown("## 📊 Financial Overview")

card1, card2, card3, card4 = st.columns(4)

with card1:
    st.markdown(
        f"""
        <div class="premium-metric metric-green">
            <div class="metric-icon">💰</div>
            <div class="metric-label">Monthly Spending</div>
            <div class="metric-value">{currency} {total_monthly:,.0f}</div>
            <div class="metric-note">Your estimated monthly cost</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card2:
    st.markdown(
        f"""
        <div class="premium-metric metric-orange">
            <div class="metric-icon">🔥</div>
            <div class="metric-label">Active Habits</div>
            <div class="metric-value">{len(habits)}</div>
            <div class="metric-note">Habits currently being tracked</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card3:
    st.markdown(
        f"""
        <div class="premium-metric metric-blue">
            <div class="metric-icon">📈</div>
            <div class="metric-label">20 Year Potential</div>
            <div class="metric-value metric-value-small">
                {currency} {future:,.0f}
            </div>
            <div class="metric-note">Potential future investment value</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with card4:
    st.markdown(
        f"""
        <div class="premium-metric metric-purple">
            <div class="metric-icon">🏆</div>
            <div class="metric-label">Financial Score</div>
            <div class="metric-value">{score}/100</div>
            <div class="metric-note">Your current financial health</div>
        </div>
        """,
        unsafe_allow_html=True,
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
        top_amount = category_spending.max()

        st.markdown(
            f"""
            <div class="spending-highlight">
            <div class="spending-highlight-icon">🏆</div>
            <div class="spending-highlight-label">
                Highest Spending Category
            </div>
            <div class="spending-highlight-value">
                {top_category}
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="spending-highlight spending-highlight-money">
            <div class="spending-highlight-icon">💸</div>
            <div class="spending-highlight-label">
                Monthly Amount
            </div>
            <div class="spending-highlight-value">
                {currency} {top_amount:,.0f}
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )




else:

    st.info(
        "Add habits to view your spending breakdown."
    )


st.markdown(
    '<div class="home-footer"><div class="home-footer-brand">HabitCost</div><div class="home-footer-tagline">Track habits • Understand spending • Build wealth</div><div class="home-footer-note">Version 1.0 • Built with ❤️</div></div>',
    unsafe_allow_html=True,
)