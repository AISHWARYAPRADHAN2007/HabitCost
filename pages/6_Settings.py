import streamlit as st

from auth import get_user

from database import (
    supabase,
    get_profile,
    save_profile,
)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Settings | HabitCost",
    page_icon="⚙️",
    layout="wide",
)


# ==========================================
# LOAD SHARED CSS
# ==========================================

def load_css():
    try:
        with open("assets/style.css", encoding="utf-8") as css_file:
            st.markdown(
                f"<style>{css_file.read()}</style>",
                unsafe_allow_html=True,
            )
    except FileNotFoundError:
        st.warning("The assets/style.css file could not be found.")


load_css()


# ==========================================
# HOME BUTTON
# ==========================================

if st.button(
    "🏠 Home",
    key="settings_home_button",
):
    st.switch_page("app.py")


# ==========================================
# LOGIN CHECK
# ==========================================

if "user" not in st.session_state:
    st.session_state.user = get_user()

if st.session_state.user is None:
    st.warning("Please log in first.")
    st.stop()

user_email = st.session_state.user.email


# ==========================================
# RESTORE SUPABASE SESSION
# ==========================================

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
        st.warning("Your session has expired. Please log in again.")
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
        "notes": "",
    }


# ==========================================
# SAFE PROFILE VALUES
# ==========================================

profile_income = int(profile.get("income") or 0)

profile_currency = profile.get("currency") or "INR"

profile_investment_rate = int(
    profile.get("investment_rate") or 10
)

profile_monthly_budget = int(
    profile.get("monthly_budget") or 0
)

profile_goal = profile.get("goal") or "Save More"

profile_notes = profile.get("notes") or ""


# ==========================================
# PAGE HEADER
# ==========================================

st.markdown(
    '<div class="settings-page-header"><div class="settings-page-eyebrow">⚙️ ACCOUNT PREFERENCES</div><div class="settings-page-title">Settings</div><div class="settings-page-subtitle">Manage your personal profile, financial preferences, goals, and account access.</div></div>',
    unsafe_allow_html=True,
)


# ==========================================
# PROFILE OVERVIEW
# ==========================================

st.markdown(
    '<div class="section-header"><div class="section-title">👤 Profile Overview</div><div class="section-subtitle">Your account identity and current financial configuration.</div></div>',
    unsafe_allow_html=True,
)

profile_col, status_col = st.columns([1.6, 1])

with profile_col:
    st.markdown(
        f'<div class="settings-profile-card"><div class="settings-profile-avatar">👤</div><div class="settings-profile-content"><div class="settings-profile-label">Signed in as</div><div class="settings-profile-email">{user_email}</div><div class="settings-profile-note">Your email address is connected to your HabitCost account and cannot be edited here.</div></div></div>',
        unsafe_allow_html=True,
    )

with status_col:
    st.markdown(
        f'<div class="settings-status-card"><div class="settings-status-top"><div class="settings-status-icon">✅</div><div><div class="settings-status-title">Account Active</div><div class="settings-status-subtitle">Profile successfully connected</div></div></div><div class="settings-status-row"><span>Currency</span><strong>{profile_currency}</strong></div><div class="settings-status-row"><span>Primary goal</span><strong>{profile_goal}</strong></div></div>',
        unsafe_allow_html=True,
    )


# ==========================================
# SETTINGS FORM
# ==========================================

st.markdown(
    '<div class="section-header"><div class="section-title">💰 Financial Preferences</div><div class="section-subtitle">These values are used throughout your dashboard, reports, and investment projections.</div></div>',
    unsafe_allow_html=True,
)

currency_options = [
    "INR",
    "AED",
    "USD",
    "EUR",
    "GBP",
]

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

currency_index = (
    currency_options.index(profile_currency)
    if profile_currency in currency_options
    else 0
)

goal_index = (
    goal_options.index(profile_goal)
    if profile_goal in goal_options
    else 0
)

with st.form(
    "financial_settings_form",
    clear_on_submit=False,
):

    financial_left, financial_right = st.columns(2)

    with financial_left:
        st.markdown(
            '<div class="settings-field-card"><div class="settings-field-icon">💵</div><div class="settings-field-title">Income &amp; Budget</div><div class="settings-field-description">Set your regular monthly income and preferred spending limit.</div></div>',
            unsafe_allow_html=True,
        )

        income = st.number_input(
            "Monthly Income",
            min_value=0,
            value=profile_income,
            step=500,
            help="Enter your approximate monthly income.",
        )

        monthly_budget = st.number_input(
            "Monthly Budget",
            min_value=0,
            value=profile_monthly_budget,
            step=500,
            help="Set the maximum amount you want to spend each month.",
        )

    with financial_right:
        st.markdown(
            '<div class="settings-field-card"><div class="settings-field-icon">📈</div><div class="settings-field-title">Currency &amp; Returns</div><div class="settings-field-description">Choose your default currency and estimated annual investment return.</div></div>',
            unsafe_allow_html=True,
        )

        currency = st.selectbox(
            "Currency",
            currency_options,
            index=currency_index,
            help="This currency will be used across HabitCost.",
        )

        investment_rate = st.slider(
            "Default Investment Return (%)",
            min_value=1,
            max_value=20,
            value=max(
                1,
                min(20, profile_investment_rate),
            ),
            help="Used for investment opportunity-cost projections.",
        )

    st.markdown(
        '<div class="settings-form-separator"></div>',
        unsafe_allow_html=True,
    )

    goal_col, notes_col = st.columns([1, 1.4])

    with goal_col:
        st.markdown(
            '<div class="settings-field-card settings-goal-intro"><div class="settings-field-icon">🎯</div><div class="settings-field-title">Primary Goal</div><div class="settings-field-description">Select the financial objective you currently want to prioritise.</div></div>',
            unsafe_allow_html=True,
        )

        goal = st.selectbox(
            "Primary Financial Goal",
            goal_options,
            index=goal_index,
            label_visibility="collapsed",
        )

    with notes_col:
        st.markdown(
            '<div class="settings-field-card settings-notes-intro"><div class="settings-field-icon">📝</div><div class="settings-field-title">Personal Notes</div><div class="settings-field-description">Keep reminders, ideas, or short notes related to your financial plan.</div></div>',
            unsafe_allow_html=True,
        )

        notes = st.text_area(
            "Personal Notes",
            value=profile_notes,
            height=145,
            placeholder="For example: Reduce food delivery spending and save for a new laptop.",
            label_visibility="collapsed",
        )

    save_settings = st.form_submit_button(
        "💾 Save Settings",
        use_container_width=True,
        type="primary",
    )


# ==========================================
# SAVE SETTINGS
# ==========================================

if save_settings:

    try:
        save_profile(
            user_email,
            income,
            currency,
            investment_rate,
            monthly_budget,
            goal,
            notes,
        )

        st.success("Settings updated successfully!")
        st.rerun()

    except Exception as error:
        st.error(
            f"Settings could not be saved: {error}"
        )


# ==========================================
# ACCOUNT SECTION
# ==========================================

st.markdown(
    '<div class="section-header"><div class="section-title">🔐 Account &amp; Security</div><div class="section-subtitle">Manage your active session and account access.</div></div>',
    unsafe_allow_html=True,
)

logout_col, delete_col = st.columns(2)

with logout_col:
    st.markdown(
        '<div class="settings-account-card settings-logout-card"><div class="settings-account-icon">🚪</div><div class="settings-account-title">Sign Out</div><div class="settings-account-description">End the current session on this device. Your saved financial data will remain secure.</div></div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "🚪 Logout",
        use_container_width=True,
        key="settings_logout_button",
    ):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.clear()

        st.success("Logged out successfully.")
        st.rerun()

with delete_col:
    st.markdown(
        '<div class="settings-account-card settings-delete-card"><div class="settings-account-icon">🗑️</div><div class="settings-account-title">Delete Account</div><div class="settings-account-description">Permanent account deletion is not currently available. This feature will be added in a future update.</div><div class="settings-coming-soon">COMING SOON</div></div>',
        unsafe_allow_html=True,
    )


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    '<div class="settings-footer"><div class="settings-footer-brand">HabitCost Settings</div><div class="settings-footer-tagline">Personalised for better financial decisions</div><div class="settings-footer-note">Changes to your financial preferences affect calculations and projections across the application.</div></div>',
    unsafe_allow_html=True,
)