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
if st.button("🏠 Home"):
    st.switch_page("app.py")

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Analytics",
    page_icon="📈",
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

st.title(
    "📈 Analytics"
)

st.caption(
    "Understand your spending patterns and habit impact."
)


st.divider()

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
    st.metric(
        "Monthly Spending",
        f"₹ {total_monthly:,.0f}"
    )

with c2:
    st.metric(
        "Categories",
        len(category_data)
    )

with c3:
    st.metric(
        "Costliest Habit",
        highest_habit
    )



# ==========================================
# SPENDING BY CATEGORY
# ==========================================

st.divider()

st.subheader(
    "💸 Spending by Category"
)




chart_col, info_col = st.columns([2,1])


with chart_col:
    category_chart = (
    category_data
    .reset_index()
    )

    category_chart.columns = [
    "Category",
    "Monthly Cost"
    ]

    fig = px.bar(
    category_chart,
    x="Category",
    y="Monthly Cost",
    color="Category",
    text_auto=True,
    title="Monthly Spending by Category"
    )

    fig.update_layout(
    xaxis_title="",
    yaxis_title="Monthly Cost (₹)",
    height=450
    )

    st.plotly_chart(
    fig,
    use_container_width=True
    )

    

with info_col:

    st.markdown(
        "### 🏆 Top Spending"
    )

    highest_category = (
        category_data.idxmax()
    )

    highest_amount = (
        category_data.max()
    )


    st.metric(
        highest_category,
        f"₹ {highest_amount:,.0f}/month"
    )


    st.write("")


    st.markdown(
        "### 📌 Breakdown"
    )


    for category, amount in category_data.items():

        percentage = (
            amount /
            category_data.sum()
            *
            100
        )

        st.write(
            f"{category}: {percentage:.1f}%"
        )

        st.progress(
            percentage / 100
        )



# ==========================================
# HABIT IMPACT
# ==========================================

st.divider()

st.subheader(
    "🔥 Habit Impact Comparison"
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
        ## {category_icons.get(category,'💸')} {category}

        Monthly: **₹ {monthly_total:,.0f}**
        
        Yearly: **₹ {yearly_total:,.0f}**
        """
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

    st.dataframe(
        table_df,
        hide_index=True,
        use_container_width=True
    )


st.divider()



# ==========================================
# SPENDING BREAKDOWN
# ==========================================


st.divider()

st.subheader(
    "📊 Spending Breakdown"
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
        ### {category}

        ₹ {amount:,.0f} / month

        {percentage:.1f}% of total spending
        """
    )

    st.progress(
        percentage / 100
    )


# ==========================================
# HISTORY TRENDS
# ==========================================

st.divider()

st.subheader(
    "📈 Spending History"
)


snapshots = get_month_snapshots(
    user_email
)


if snapshots:

    history_df = pd.DataFrame(
        snapshots
    )


    history_df = history_df.sort_values(
        "month"
    )


    history_chart = history_df.rename(
    columns={
        "month": "Month",
        "spending": "Monthly Spending"
    }
    )

    fig = px.line(
    history_chart,
    x="Month",
    y="Monthly Spending",
    markers=True,
    title="Monthly Spending Trend"
    )

    fig.update_layout(
    xaxis_title="",
    yaxis_title="Monthly Spending (₹)",
    height=450
    )

    st.plotly_chart(
    fig,
    use_container_width=True
    )


else:

    st.info(
        "No monthly history available yet."
    )
    
st.divider()

