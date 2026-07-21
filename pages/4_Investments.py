import streamlit as st
import pandas as pd
import plotly.express as px

from auth import logout
from auth import get_user
from database import (
    supabase,
    get_habits,
    get_profile,
)
from calculations import monthly_cost


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Investments",
    page_icon="💹",
    layout="wide",
)


def load_css():
    with open("assets/style.css", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )


load_css()


if st.button(
    "🏠 Home",
    key="investments_home_button",
):
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
st.markdown(
    """
<div class="investments-page-header"><div class="investments-page-eyebrow">WEALTH BUILDER</div><div class="investments-page-title">💹 Investments</div><div class="investments-page-subtitle">Turn small habit reductions into meaningful savings, long-term investments, and future financial goals.</div></div>
""",
    unsafe_allow_html=True,
)
# ==========================================
# SAVINGS SIMULATOR
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">💰 Savings Simulator</div><div class="section-subtitle">Experiment with reducing a habit to see how much money you could save every day, month, and year.</div></div>
""",
    unsafe_allow_html=True,
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


daily_saving = monthly_saving / 30

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        f"""
<div class="investment-metric-card investment-green"><div class="investment-metric-icon">📅</div><div class="investment-metric-label">Monthly Saving</div><div class="investment-metric-value">₹ {monthly_saving:,.0f}</div><div class="investment-metric-note">Saved every month</div></div>
""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
<div class="investment-metric-card investment-blue"><div class="investment-metric-icon">💰</div><div class="investment-metric-label">Yearly Saving</div><div class="investment-metric-value">₹ {yearly_saving:,.0f}</div><div class="investment-metric-note">Saved every year</div></div>
""",
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
<div class="investment-metric-card investment-orange"><div class="investment-metric-icon">☕</div><div class="investment-metric-label">Daily Saving</div><div class="investment-metric-value">₹ {daily_saving:,.0f}</div><div class="investment-metric-note">Average per day</div></div>
""",
        unsafe_allow_html=True,
    )
st.divider()
# ==========================================
# FUTURE VALUE PREDICTION
# ==========================================


st.markdown(
    """
<div class="section-header"><div class="section-title">🔮 Future Value Prediction</div><div class="section-subtitle">Estimate how your monthly savings can grow through consistent investing and compound returns.</div></div>
""",
    unsafe_allow_html=True,
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

amount_invested = monthly_saving * months
interest_earned = future_value - amount_invested

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        f"""
<div class="future-value-card future-blue"><div class="future-icon">💸</div><div class="future-label">Monthly Investment</div><div class="future-value">₹ {monthly_saving:,.0f}</div><div class="future-note">Invested every month</div></div>
""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
<div class="future-value-card future-green"><div class="future-icon">🚀</div><div class="future-label">Future Value</div><div class="future-value">₹ {future_value:,.0f}</div><div class="future-note">Projected portfolio value</div></div>
""",
        unsafe_allow_html=True,
    )

c3, c4 = st.columns(2)

with c3:
    st.markdown(
        f"""
<div class="future-value-card future-purple"><div class="future-icon">🏦</div><div class="future-label">Total Invested</div><div class="future-value">₹ {amount_invested:,.0f}</div><div class="future-note">Your own contributions</div></div>
""",
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f"""
<div class="future-value-card future-orange"><div class="future-icon">📈</div><div class="future-label">Interest Earned</div><div class="future-value">₹ {interest_earned:,.0f}</div><div class="future-note">Growth from compounding</div></div>
""",
        unsafe_allow_html=True,
    )

# ==========================================
# INVESTMENT GROWTH CHART
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">📈 Investment Growth</div><div class="section-subtitle">Visualize how consistent monthly investing can compound over time.</div></div>
""",
    unsafe_allow_html=True,
)

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

fig = px.line(
    growth_df,
    x="Year",
    y="Value",
    markers=True,
)

fig.update_traces(
    line=dict(
        width=4,
        color="#22C55E",
    ),
    marker=dict(
        size=9,
        color="#4ADE80",
        line=dict(
            width=2,
            color="#F8FAFC",
        ),
    ),
    fill="tozeroy",
    fillcolor="rgba(34,197,94,0.08)",
    hovertemplate="<b>Year %{x}</b><br>₹ %{y:,.0f}<extra></extra>",
)

fig.update_layout(
    height=460,
    margin=dict(
        l=10,
        r=10,
        t=25,
        b=10,
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="#CBD5E1",
    ),
    xaxis=dict(
        title="Investment Year",
        showgrid=False,
        dtick=1,
        tickfont=dict(
            color="#CBD5E1",
        ),
    ),
    yaxis=dict(
        title="Portfolio Value (₹)",
        gridcolor="rgba(148,163,184,0.12)",
        zeroline=False,
        tickprefix="₹ ",
        tickformat=",",
    ),
    hovermode="x unified",
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
    },
)
# ==========================================
# SCENARIO COMPARISON
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">📊 Investment Scenarios</div><div class="section-subtitle">Compare how the same monthly investment could grow across different time horizons.</div></div>
""",
    unsafe_allow_html=True,
)

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


comparison_df = pd.DataFrame(comparison)

scenario_cols = st.columns(len(comparison_df))

for index, row in comparison_df.iterrows():
    with scenario_cols[index]:
        st.markdown(
            f"""
<div class="scenario-card"><div class="scenario-icon">⏳</div><div class="scenario-years">{row["Years"]} Years</div><div class="scenario-label">Projected Value</div><div class="scenario-value">{row["Future Value"]}</div><div class="scenario-note">Based on {rate}% annual return</div></div>
""",
            unsafe_allow_html=True,
        )

# ==========================================
# INVESTMENT INSIGHT
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">💡 Investment Insight</div><div class="section-subtitle">See the long-term impact of reducing a habit and investing the savings consistently.</div></div>
""",
    unsafe_allow_html=True,
)


st.markdown(
    f"""
<div class="investment-insight-card"><div class="investment-insight-icon">💡</div><div class="investment-insight-title">Your Investment Opportunity</div><div class="investment-insight-text">Reducing <strong>{selected_habit}</strong> by <strong>{reduction}%</strong> saves you <strong>₹ {monthly_saving:,.0f}</strong> every month.</div><div class="investment-insight-text">Investing that amount for <strong>{years} years</strong> at an expected <strong>{rate}% annual return</strong> could grow your money into:</div><div class="investment-insight-result">💰 ₹ {future_value:,.0f}</div></div>
""",
    unsafe_allow_html=True,
)
profile = get_profile(user_email)
if profile:
    st.markdown(
        f"""
<div class="investment-goal-card"><div class="investment-goal-title">🎯 Current Goal</div><div class="investment-goal-name">{profile.get("goal", 0)}</div><div class="investment-goal-text">Stay consistent with your investments to move closer to achieving this goal.</div></div>
""",
        unsafe_allow_html=True,
    )
# ==========================================
# WHAT COULD THIS BECOME?
# ==========================================

st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">🎯 What Could This Become?</div><div class="section-subtitle">Translate your future investment value into real-world goals and possibilities.</div></div>
""",
    unsafe_allow_html=True,
)


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
    st.markdown(
        f"""
<div class="possibility-highlight"><div class="possibility-highlight-icon">✨</div><div><div class="possibility-highlight-title">Your money could become something meaningful</div><div class="possibility-highlight-text">A projected value of <strong>₹ {future_value:,.0f}</strong> can unlock these possibilities:</div></div></div>
""",
        unsafe_allow_html=True,
    )

    possibility_cols = st.columns(2)

    for index, item in enumerate(ideas):
        with possibility_cols[index % 2]:
            st.markdown(
                f"""
<div class="possibility-card"><div class="possibility-number">{index + 1}</div><div class="possibility-text">{item}</div></div>
""",
                unsafe_allow_html=True,
            )

else:
    st.markdown(
        """
<div class="possibility-empty"><div class="possibility-empty-icon">🌱</div><div class="possibility-empty-title">Every investment starts small</div><div class="possibility-empty-text">Keep investing consistently and your future possibilities will continue to grow.</div></div>
""",
        unsafe_allow_html=True,
    )
profile = get_profile(user_email)

if profile:

    goal = profile.get("goal", 0)

    st.divider()

    st.markdown(
    """
    <div class="section-header"><div class="section-title">🎯 Goal Progress</div><div class="section-subtitle">Stay focused on your financial objective and see how consistent investing supports it.</div></div>
    """,
       unsafe_allow_html=True,
    )

    st.markdown(
    f"""
    <div class="goal-progress-card"><div class="goal-progress-icon">🎯</div><div class="goal-progress-label">Current Financial Goal</div><div class="goal-progress-title">{goal}</div></div>
    """,
       unsafe_allow_html=True,
    )

    if goal == "Save More":
        goal_tip = "💰 Continue investing consistently to grow your savings."

    elif goal == "Reduce Spending":
        goal_tip = "📉 Every unnecessary habit you reduce moves you closer to this goal."

    elif goal == "Build Emergency Fund":
       goal_tip = "🛟 Build at least 6 months of expenses for financial security."

    elif goal == "Travel":
       goal_tip = "✈️ Your investments can become your next vacation fund."

    elif goal == "Buy a Laptop":
       goal_tip = "💻 Keep investing until you can buy your laptop without debt."

    elif goal == "Buy a Vehicle":
       goal_tip = "🏍️ Your monthly investments can become a vehicle down payment."

    elif goal == "Buy a House":
       goal_tip = "🏠 Long-term investing is a great way to build a home down payment."

    elif goal == "Invest More":
       goal_tip = "📈 Increase your SIP whenever your income increases."

    elif goal == "Education":
       goal_tip = "🎓 Your investments can fund future studies and certifications."

    else:
       goal_tip = "🌟 Stay consistent. Every investment brings you closer to your goal."

    st.markdown(
    f"""
<div class="goal-progress-tip">{goal_tip}</div>
""",
    unsafe_allow_html=True,
    )
st.divider()

st.markdown(
    """
<div class="section-header"><div class="section-title">📚 Investment Tips</div><div class="section-subtitle">Simple principles that help your investments grow steadily over time.</div></div>
""",
    unsafe_allow_html=True,
)

tips = [
    "💡 Invest every month, even if it's a small amount.",
    "📈 The earlier you start, the more compounding works for you.",
    "💰 Increase investments whenever your salary increases.",
    "🚫 Avoid withdrawing investments unless absolutely necessary.",
    "🎯 Stay consistent rather than trying to time the market."
]

tip_cols = st.columns(2)

for index, tip in enumerate(tips):
    with tip_cols[index % 2]:
        st.markdown(
            f"""
<div class="investment-tip-card"><div class="investment-tip-number">{index + 1}</div><div class="investment-tip-text">{tip}</div></div>
""",
            unsafe_allow_html=True,
        )
st.markdown(
    """
<div class="investments-footer"><div class="investments-footer-brand">HabitCost Investments</div><div class="investments-footer-tagline">Reduce wasteful habits. Build meaningful wealth.</div><div class="investments-footer-note">All projections are estimates and actual returns may vary.</div></div>
""",
    unsafe_allow_html=True,
)
