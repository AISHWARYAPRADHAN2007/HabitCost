import plotly.express as px


def spending_history_chart(history):

    if not history:
        return None


    months = [x["month"] for x in history]
    spending = [x["spending"] for x in history]


    fig = px.line(
        x=months,
        y=spending,
        markers=True,
        labels={
            "x": "Month",
            "y": "Monthly Spending"
        },
        title="📈 Spending Trend"
    )


    return fig



def habit_history_chart(history):

    if not history:
        return None


    months = [x["month"] for x in history]
    habits = [x["habits"] for x in history]


    fig = px.bar(
        x=months,
        y=habits,
        labels={
            "x": "Month",
            "y": "Number of Habits"
        },
        title="📊 Habit Count Trend"
    )


    return fig