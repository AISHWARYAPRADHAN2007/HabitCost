import streamlit as st
from auth import logout
from auth import get_user

from database import (
    supabase,
    get_profile,
    save_profile,
)
if st.button("🏠 Home"):
    st.switch_page("app.py")
# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
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
            st.session_state.session.refresh_token,
        )

    except:

        st.warning("Session expired.")
        st.stop()


# ==========================================
# LOAD PROFILE
# ==========================================

profile = get_profile(user_email)



if profile is None:

    profile = {
        "income": 0,
        "currency": "INR",
        "investment_rate": 10,
        "monthly_budget": 0,
        "goal": "Save More",
        
        
    }


# ==========================================
# TITLE
# ==========================================

st.title("⚙️ Settings")

st.caption(
    "Manage your financial preferences."
)

st.divider()


# ==========================================
# PROFILE
# ==========================================

st.subheader("👤 Profile")

st.text_input(
    "Email",
    value=user_email,
    disabled=True
)

st.divider()


# ==========================================
# FINANCIAL SETTINGS
# ==========================================

st.subheader("💰 Financial Preferences")

income = st.number_input(
    "Monthly Income",
    min_value=0,
    value=int(profile["income"])
)

currency_options = [
    "INR",
    "AED",
    "USD",
    "EUR",
    "GBP"
]

currency = st.selectbox(
    "Currency",
    currency_options,
    index=currency_options.index(
        profile.get("currency", "INR")
    )
    if profile.get("currency", "INR") in currency_options
    else 0
)

investment_rate = st.slider(
    "Default Investment Return (%)",
    1,
    20,
    int(profile["investment_rate"])
)

monthly_budget = st.number_input(
    "Monthly Budget",
    min_value=0,
    value=int(profile["monthly_budget"])
)

st.divider()

# ==========================================
# GOAL
# ==========================================

goal_options = [
    "Save More",
    "Reduce Spending",
    "Build Emergency Fund",
    "Travel",
    "Buy a Laptop",
    "Buy a Vehicle",
    "Buy a House",
    "Invest More",
    "Education",
    "Other",
]

goal = st.selectbox(
    "🎯 Primary Financial Goal",
    goal_options,
    index=goal_options.index(
        profile.get("goal", "Save More")
    ),
)

st.subheader("📝 Personal Notes")

notes = st.text_area(
    "Write reminders or financial notes",
    value=profile.get("notes", ""),
    height=180
)

# ==========================================
# SAVE
# ==========================================

if st.button(
    "💾 Save Settings",
    use_container_width=True
):

    save_profile(
        user_email,
        income,
        currency,
        investment_rate,
        monthly_budget,
        goal,
    )

    st.success(
        "Settings updated successfully!"
    )

    st.rerun()


# ==========================================
# ACCOUNT
# ==========================================

st.divider()

st.subheader("🔐 Account")

if st.button(
    "🚪 Logout",
    use_container_width=True
):

    supabase.auth.sign_out()

    st.session_state.clear()

    st.success(
        "Logged out successfully."
    )

    st.rerun()


st.info(
    "Delete account feature coming soon."
)

st.divider()

