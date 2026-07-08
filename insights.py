def generate_insights(df, future_20):

    insights = []

    total_monthly = df["Monthly Cost"].sum()

    biggest = df.loc[df["Monthly Cost"].idxmax()]

    percentage = (
        biggest["Monthly Cost"] /
        total_monthly
    ) * 100

    category = (
        df.groupby("Category")["Monthly Cost"]
        .sum()
        .idxmax()
    )

    insights.append(
        f"⚠️ {biggest['Habit'].title()} is your biggest expense, making up {percentage:.1f}% of your monthly spending."
    )

    insights.append(
        f"💸 It costs you ₹{biggest['Yearly Cost']:,.0f} every year."
    )

    insights.append(
        f"📊 Your highest spending category is {category}."
    )

    insights.append(
        f"💰 Investing your current monthly habit expenses for 20 years at your selected return could grow to about ₹{future_20:,.0f}."
    )

    return insights