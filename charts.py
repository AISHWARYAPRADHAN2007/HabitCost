import plotly.express as px


def spending_pie_chart(df):

    fig = px.pie(
        df, names="Habit", values="Monthly Cost", title="Monthly Spending Breakdown"
    )

    fig.update_traces(textinfo="percent+label")

    return fig


import plotly.express as px


def category_bar_chart(df):

    category_df = df.groupby("Category")["Monthly Cost"].sum().reset_index()

    fig = px.bar(
        category_df,
        x="Category",
        y="Monthly Cost",
        color="Category",
        title="Monthly Spending by Category",
    )

    return fig
