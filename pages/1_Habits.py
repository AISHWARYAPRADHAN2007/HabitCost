import streamlit as st
import pandas as pd
import calendar
from datetime import date
from auth import logout

from auth import get_user
from database import (
    supabase,
    get_habits,
    get_habit_logs,
    add_habit_log,
    add_habit,
    delete_habit,
    update_habit,
)

from calculations import (
    monthly_cost,
    should_show_habit,
)




# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Habits",
    page_icon="💸",
    layout="wide"
)

def load_css():
    with open("assets/style.css", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )


load_css()

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

    except Exception:
       st.warning("Session expired. Please login again.")
       st.stop()

# ==========================================
# LOAD HABITS
# ==========================================

habits = get_habits(user_email)

df = pd.DataFrame(habits)

if df.empty:
    df = pd.DataFrame(
        columns=[
            "id",
            "habit",
            "category",
            "cost",
            "frequency",
            "tracking_type",
            "billing_day",
            "start_date",
        ]
    )

# ==========================================
# SESSION STATE
# ==========================================

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

if "month" not in st.session_state:
    st.session_state.month = date.today().month

if "year" not in st.session_state:
    st.session_state.year = date.today().year
if "habit_added" not in st.session_state:
    st.session_state.habit_added = False
# ==========================================
# TITLE
# ==========================================
st.markdown(
    """
<div class="habits-page-header"><div class="habits-page-eyebrow">HABIT TRACKER</div><div class="habits-page-title">💸 Your Habits</div><div class="habits-page-subtitle">Track daily choices and understand their financial impact.</div></div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# CALENDAR
# ==========================================

left, middle, right = st.columns([1, 5, 1])

with left:
    if st.button("⬅", use_container_width=True):

        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1


        st.rerun()


with middle:

    st.markdown(
        f"""
        <h2 style='text-align:center'>
        📅 {calendar.month_name[st.session_state.month]} {st.session_state.year}
        </h2>
        """,
        unsafe_allow_html=True
    )


with right:

    if st.button("➡", use_container_width=True):

        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1

        st.rerun()


st.write("")


# Weekday headers
days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

cols = st.columns(7)

for col, day in zip(cols, days):
    col.markdown(
        f"""
<div class="calendar-day-header">
{day}
</div>
""",
        unsafe_allow_html=True,
    )

# Calendar Grid
month = calendar.monthcalendar(
    st.session_state.year,
    st.session_state.month
)

for week in month:

    cols = st.columns(7)

    for i, day in enumerate(week):

        with cols[i]:

            if day == 0:

                st.write("")

            else:

                current_day = date(
                    st.session_state.year,
                    st.session_state.month,
                    day
                )

                if current_day == st.session_state.selected_date:

                    label = f"🔵 {day}"

                else:

                    label = str(day)

                if st.button(
                    label,
                    use_container_width=True,
                    key=f"day_{current_day}"
                ):

                    st.session_state.selected_date = current_day

                    st.rerun()
                    
st.divider()

st.subheader(
    st.session_state.selected_date.strftime("%d %B %Y")
)

st.divider()

# ==========================================
# TODAY'S HABITS
# ==========================================

logs = get_habit_logs(
    user_email,
    st.session_state.selected_date
)


completed_ids = {
    log["habit_id"]
    for log in logs
    if log["completed"]
}

# Convert costs
display_df = df.rename(
    columns={
        "habit": "Habit",
        "category": "Category",
        "cost": "Cost",
        "frequency": "Frequency",
        "tracking_type": "Tracking_Type",
        "billing_day": "Billing_Day",
        "start_date": "Start_Date",
    }
).copy()


display_df["Monthly Cost"] = display_df.apply(
    lambda row: monthly_cost(
        row["Cost"],
        row["Frequency"]
    ),
    axis=1
)

if display_df.empty:

    visible_habits = display_df.copy()

else:

    visible_habits = display_df[
        display_df.apply(
            lambda row: should_show_habit(
                row,
                st.session_state.selected_date
            ),
            axis=1,
        )
    ]

# ==========================================
# DAILY SUMMARY
# ==========================================

completed_count = len(completed_ids)

total_count = len(visible_habits)

planned_today = visible_habits["Cost"].sum()

spent_today = visible_habits[
    visible_habits["id"].isin(completed_ids)
]["Cost"].sum()

progress = (
    completed_count / total_count
    if total_count > 0
    else 0
)
st.markdown("### Daily Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="habit-summary-card habit-summary-purple">
            <div class="habit-summary-icon">💰</div>
            <div class="habit-summary-label">Planned Today</div>
            <div class="habit-summary-value">₹ {planned_today:,.0f}</div>
            <div class="habit-summary-note">Expected spending</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="habit-summary-card habit-summary-orange">
            <div class="habit-summary-icon">💸</div>
            <div class="habit-summary-label">Spent Today</div>
            <div class="habit-summary-value">₹ {spent_today:,.0f}</div>
            <div class="habit-summary-note">Completed habit cost</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="habit-summary-card habit-summary-green">
            <div class="habit-summary-icon">✅</div>
            <div class="habit-summary-label">Completed</div>
            <div class="habit-summary-value">
                {completed_count}/{total_count}
            </div>
            <div class="habit-summary-note">Habits finished today</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="habit-summary-card habit-summary-blue">
            <div class="habit-summary-icon">📈</div>
            <div class="habit-summary-label">Progress</div>
            <div class="habit-summary-value">
                {progress * 100:.0f}%
            </div>
            <div class="habit-summary-note">Daily completion rate</div>
        </div>
        """,
        unsafe_allow_html=True,

    )
st.markdown(
    f"""
<div style="
display:flex;
justify-content:space-between;
align-items:center;
font-size:18px;
font-weight:700;
color:#E2E8F0;
margin-bottom:10px;
">
<span>📈 Daily Progress</span>
<span>{progress*100:.0f}%</span>
</div>
""",
    unsafe_allow_html=True,
)

st.progress(progress)

st.divider()

# ==========================================
# TODAY'S HABITS
# ==========================================
if st.session_state.habit_added:
    st.success("✅ Habit added successfully!")
    st.session_state.habit_added = False
with st.expander("➕ Add New Habit", expanded=False):
    
    st.caption(
        "Create a habit and start tracking its financial impact."
    )
    
    with st.form("add_habit_form"):

        habit_name = st.text_input("Habit Name")

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
                "Other" 
            ]
        )

        cost = st.number_input(
            "Cost",
            min_value=0.0,
            step=1.0
        )

        frequency = st.selectbox(
            "Frequency",
            [
                "Daily",
                "Weekly",
                "Monthly",
                "Yearly"
            ]
        )

        tracking_type = st.selectbox(
            "Tracking Method",
            [
                "Automatic",
                "Manual"
            ]
        )

        billing_day = None

        if frequency in ["Monthly", "Yearly"]:
            billing_day = st.number_input(
                "Billing Day",
                min_value=1,
                max_value=31,
                value=1
            )

        submitted = st.form_submit_button(
            "➕ Add Habit",
            use_container_width=True
        )

        if submitted:

            if habit_name.strip() == "":
                st.warning("Please enter a habit name.")

            else:
                try:
                    
                    add_habit(
                        user_email,
                        {
                            "Habit": habit_name.strip(),
                            "Category": category,
                            "Cost": float(cost),
                            "Frequency": frequency,
                            "Tracking_Type": tracking_type.lower(),
                            "Billing_Day": billing_day,
                        }
                    )

                    st.session_state.habit_added = True

                    st.rerun()

                except Exception as e:

                    st.error(e)

                
        
# ==========================================
# TODAY'S HABITS
# ==========================================

st.header("Today's Habits")

if visible_habits.empty:

    st.info("🎉 No habits scheduled for this day.")

else:

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

    if "editing_habit" not in st.session_state:
        st.session_state.editing_habit = None

    # ==========================================
    # SEARCH + FILTER
    # ==========================================

    search = st.text_input(
        "🔍 Search habits",
        placeholder="Search your habits..."
    )

    filter_category = st.selectbox(
        "Filter Category",
        ["All"] + sorted(
            visible_habits["Category"].unique().tolist()
        )
    )

    filtered_habits = visible_habits.copy()

    if search:

        filtered_habits = filtered_habits[
            filtered_habits["Habit"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    if filter_category != "All":

        filtered_habits = filtered_habits[
            filtered_habits["Category"] == filter_category
        ]

    if filtered_habits.empty:

        st.info("No habits match your search.")
        st.stop()

    # ==========================================
    # CATEGORY GROUPS
    # ==========================================

    for category in sorted(filtered_habits["Category"].unique()):

        category_habits = filtered_habits[
            filtered_habits["Category"] == category
        ]

        category_monthly_cost = category_habits["Monthly Cost"].sum()

        
        st.markdown(
            f"""
        <div style="font-size:32px;font-weight:700;color:white;text-shadow:0 0 18px rgba(139,92,246,.20);">{habit_icons.get(category,"💸")} {category} <span style="font-size:18px;color:#94A3B8;">({len(category_habits)} habits)</span></div><div style="font-size:18px;color:#CBD5E1;margin-top:6px;">Monthly impact: <b>₹ {category_monthly_cost:,.0f}</b></div>
        """,
        unsafe_allow_html=True,
        )
            

        with st.expander("View Habits", expanded=True):

            for _, habit in category_habits.iterrows():

                checked = habit["id"] in completed_ids

                col1, col2, col3, col4, col5 = st.columns(
                    [1,5,2,1,1]
                )

                # Checkbox

                with col1:

                    tick = st.checkbox(
                        "",
                        value=checked,
                        key=f"log_{habit['id']}"
                    )

                    if tick != checked:

                        add_habit_log(
                            user_email,
                            habit["id"],
                            st.session_state.selected_date,
                            tick,
                            habit["Cost"]
                        )

                        st.rerun()

                # Habit Name

                with col2:

                    st.markdown(
                        f"""
                        <span style="font-size:20px;font-weight:600;">
                        {habit['Habit']}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

                # Cost

                with col3:

                    st.write(
                        f"₹ {habit['Cost']:,.0f}"
                    )

                # Edit

                with col4:

                    if st.button(
                        "✏️",
                        key=f"edit_{habit['id']}"
                    ):

                        st.session_state.editing_habit = habit["id"]

                # Delete

                with col5:

                    if st.button(
                        "🗑️",
                        key=f"delete_{habit['id']}"
                    ):

                        delete_habit(
                            user_email,
                            habit["id"]
                        )

                        st.rerun()

                # ==========================================
                # EDIT FORM
                # ==========================================

                if st.session_state.editing_habit == habit["id"]:

                    with st.form(
                        f"edit_form_{habit['id']}"
                    ):

                        new_name = st.text_input(
                            "Habit Name",
                            value=habit["Habit"]
                        )

                        new_category = st.selectbox(
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
                            index=[
                                "Food",
                                "Transport",
                                "Entertainment",
                                "Shopping",
                                "Health",
                                "Subscriptions",
                                "Education",
                                "Other",
                            ].index(habit["Category"])
                        )

                        new_cost = st.number_input(
                            "Cost",
                            min_value=0.0,
                            value=float(habit["Cost"])
                        )

                        new_frequency = st.selectbox(
                            "Frequency",
                            [
                                "Daily",
                                "Weekly",
                                "Monthly",
                                "Yearly",
                            ],
                            index=[
                                "Daily",
                                "Weekly",
                                "Monthly",
                                "Yearly",
                            ].index(habit["Frequency"])
                        )

                        new_tracking = st.selectbox(
                            "Tracking Method",
                            [
                                "Automatic",
                                "Manual",
                            ],
                            index=[
                                "automatic",
                                "manual",
                            ].index(
                                habit["Tracking_Type"].lower()
                            )
                        )

                        new_billing_day = None

                        if new_frequency in ["Monthly", "Yearly"]:

                            new_billing_day = st.number_input(
                                "Billing Day",
                                min_value=1,
                                max_value=31,
                                value=int(
                                    habit["Billing_Day"] or 1
                                )
                            )

                        save = st.form_submit_button(
                            "💾 Save Changes",
                            use_container_width=True
                        )

                        if save:

                            update_habit(
                                user_email,
                                habit["id"],
                                {
                                    "Habit": new_name.strip(),
                                    "Category": new_category,
                                    "Cost": float(new_cost),
                                    "Frequency": new_frequency,
                                    "Tracking_Type": new_tracking.lower(),
                                    "Billing_Day": new_billing_day,
                                }
                            )

                            st.session_state.editing_habit = None

                            st.success(
                                "✅ Habit updated!"
                            )

                            st.rerun()

                st.divider()
st.divider()

