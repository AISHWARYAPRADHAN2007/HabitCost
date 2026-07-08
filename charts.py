import plotly.express as px


def spending_pie_chart(df):

    fig = px.pie(
        df,
        names="Habit",
        values="Monthly Cost",
        title="Monthly Spending Breakdown"
    )

    fig.update_traces(textinfo="percent+label")

    return fig