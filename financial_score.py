def calculate_score(df, monthly_income):

    if monthly_income <= 0:
        return 50, "Add income details for a better score."


    total_spending = df["Monthly Cost"].sum()


    spending_ratio = total_spending / monthly_income


    score = 100


    # Spending penalty
    if spending_ratio > 0.7:
        score -= 35

    elif spending_ratio > 0.5:
        score -= 20

    elif spending_ratio > 0.3:
        score -= 10


    # Habit count penalty
    if len(df) > 10:
        score -= 10


    # Expensive habit penalty
    if not df.empty:

        highest = df["Monthly Cost"].max()

        if highest > monthly_income * 0.1:
            score -= 10


    score = max(0, min(score, 100))


    if score >= 80:
        message = "Excellent financial habits 🌟"

    elif score >= 60:
        message = "Good, but there is room for improvement 👍"

    else:
        message = "Your spending habits need attention ⚠️"


    return score, message