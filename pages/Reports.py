from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import streamlit as st
import pandas as pd
import io
from auth import logout
from auth import get_user


from database import (
    supabase,
    get_habits,
    get_profile,
    get_month_snapshots,
)
from calculations import monthly_cost

if st.button("🏠 Home"):
    st.switch_page("app.py")

#LOGIN 

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide"
)

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

st.title("📄 Financial Report")
from datetime import datetime

st.caption(
    f"Generated on {datetime.now().strftime('%d %B %Y • %I:%M %p')}"
)
st.caption(
    "Download a summary of your spending habits."
)

st.divider()

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

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Monthly Spending",
    f"₹ {total_monthly:,.0f}"
)

c2.metric(
    "Yearly Spending",
    f"₹ {yearly:,.0f}"
)

c3.metric(
    "Top Category",
    highest
)

c4.metric(
    "Costliest Habit",
    costliest
)
#CATEGORY TABLE 

st.divider()

st.subheader("📊 Category Breakdown")

category = (
    df.groupby("category")["monthly_cost"]
    .sum()
    .reset_index()
)

category.columns = [
    "Category",
    "Monthly Cost"
]

st.dataframe(
    category,
    use_container_width=True,
    hide_index=True
)
st.divider()

st.subheader("📈 Spending History")

if snapshots:

    history_df = pd.DataFrame(snapshots)

    st.dataframe(
        history_df,
        hide_index=True,
        use_container_width=True
    )

else:

    st.info("No monthly snapshots available.")

import plotly.express as px

fig = px.pie(
    category,
    names="Category",
    values="Monthly Cost",
    title="Monthly Spending by Category"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

#PROFILE 

st.divider()

st.subheader("🎯 Financial Goal")

st.success(
    profile["goal"]
)

st.metric(
    "Monthly Budget",
    f"₹ {profile['monthly_budget']:,.0f}"
)

st.divider()

st.subheader("📋 Habit Details")

report_df = df[
    [
        "habit",
        "category",
        "cost",
        "frequency",
        "monthly_cost"
    ]
].copy()

report_df.columns = [
    "Habit",
    "Category",
    "Cost",
    "Frequency",
    "Monthly Cost"
]

report_df["Cost"] = report_df["Cost"].map(
    lambda x: f"₹ {x:,.0f}"
)

report_df["Monthly Cost"] = report_df["Monthly Cost"].map(
    lambda x: f"₹ {x:,.0f}"
)

st.dataframe(
    report_df,
    hide_index=True,
    use_container_width=True
)


st.divider()

st.subheader("📌 Report Summary")

st.info(
    f"""
• Total Monthly Spending: ₹ {total_monthly:,.0f}

• Total Yearly Spending: ₹ {yearly:,.0f}

• Highest Spending Category: {highest}

• Costliest Habit: {costliest}

• Current Financial Goal: {profile['goal']}
"""
)

# ==========================================
# CSV DOWNLOAD
# ==========================================

st.divider()

st.subheader("📥 Download CSV Report")

csv = df.to_csv(index=False)

st.download_button(
    "📥 Download CSV Report",
    data=csv,
    file_name=f"HabitCost_Report_{user_email}.csv",
    mime="text/csv",
    use_container_width=True
)

st.divider()

st.subheader("📄 Download PDF Report")

buffer = io.BytesIO()

doc = SimpleDocTemplate(buffer)

styles = getSampleStyleSheet()

story = []

story.append(
    Paragraph("<b>HabitCost Financial Report</b>", styles["Title"])
)

story.append(
    Paragraph(f"User: {user_email}", styles["Normal"])
)

story.append(
    Paragraph(f"Monthly Spending: ₹ {total_monthly:,.0f}", styles["Normal"])
)

story.append(
    Paragraph(f"Yearly Spending: ₹ {yearly:,.0f}", styles["Normal"])
)

story.append(
    Paragraph(f"Top Category: {highest}", styles["Normal"])
)

story.append(
    Paragraph(f"Costliest Habit: {costliest}", styles["Normal"])
)

story.append(
    Paragraph(
        f"Monthly Budget: ₹ {profile['monthly_budget']:,.0f}",
        styles["Normal"]
    )
)

story.append(
    Paragraph(
        f"Financial Goal: {profile['goal']}",
        styles["Normal"]
    )
)

story.append(
    Paragraph("<br/><b>Spending History</b>", styles["Heading2"])
)

if snapshots:

    for row in snapshots:

        story.append(
            Paragraph(
                f"{row['month']} : ₹ {row['spending']:,.0f}",
                styles["Normal"]
            )
        )

story.append(
    Paragraph("<br/><b>Category Breakdown</b>", styles["Heading2"])
)

for _, row in category.iterrows():

    story.append(
        Paragraph(
            f"{row['Category']} : ₹ {row['Monthly Cost']:,.0f}",
            styles["Normal"]
        )
    )
story.append(
    Paragraph("<br/><b>Habit Details</b>", styles["Heading2"])
)

for _, row in report_df.iterrows():

    story.append(
        Paragraph(
            f"{row['Habit']} | {row['Category']} | {row['Monthly Cost']}",
            styles["Normal"]
        )
    )

story.append(
    Paragraph("<br/><b>Personal Notes</b>", styles["Heading2"])
)
notes = profile.get("notes")

if not notes:
    notes = "No notes"

story.append(
    Paragraph(notes, styles["Normal"])
)

doc.build(story)

buffer.seek(0)

st.download_button(
    "📄 Download PDF",
    data=buffer,
    file_name=f"HabitCost_Report_{user_email}.pdf",
    mime="application/pdf"
)

st.divider()

