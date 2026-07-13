# ==========================================
# Habit Calculations
# ==========================================

def monthly_cost(cost, frequency):

    if frequency == "Daily":
        return cost * 30

    elif frequency == "Weekly":
        return cost * 4

    elif frequency == "Monthly":
        return cost

    elif frequency == "Yearly":
        return cost / 12

    return 0


def yearly_cost(monthly):

    return monthly * 12


def five_year_cost(monthly):

    return monthly * 12 * 5


def ten_year_cost(monthly):

    return monthly * 12 * 10
# ==========================================
# Future Value Calculation
# ==========================================

def future_value(monthly_investment, annual_rate, years):

    monthly_rate = annual_rate / 100 / 12
    months = years * 12

    if monthly_rate == 0:
        return monthly_investment * months

    fv = monthly_investment * (
        ((1 + monthly_rate) ** months - 1)
        / monthly_rate
    ) * (1 + monthly_rate)

    return fv
def create_dashboard_data(habits):

    dashboard = []

    for habit in habits:

        monthly = habit["Monthly Cost"]

        yearly = monthly * 12

        twenty_year = yearly * 20

        dashboard.append({
            "Habit": habit["Habit"],
            "Monthly Cost": monthly,
            "Yearly Cost": yearly,
            "20 Year Cost": twenty_year
        })

    return dashboard

from datetime import datetime


def should_show_habit(habit, selected_date):

    frequency = habit["Frequency"]

    start_date = datetime.strptime(
        str(habit["Start_Date"]),
        "%Y-%m-%d"
    ).date()


    # Nothing before habit starts
    if selected_date < start_date:
        return False


    # Daily habits
    if frequency == "Daily":
        return True


    # Weekly habits
    if frequency == "Weekly":

        days_difference = (
            selected_date - start_date
        ).days

        return days_difference % 7 == 0


    # Monthly subscriptions
    # Show every day after starting
    if frequency == "Monthly":
        return True


    # Yearly subscriptions
    # Show every day after starting
    if frequency == "Yearly":
        return True


    return False
def financial_health_score(
    total_monthly_spending,
    total_habits,
    subscription_cost
):

    score = 100

    if total_monthly_spending > 50000:
        score -= 25

    elif total_monthly_spending > 20000:
        score -= 10

    if total_habits >= 5:
        score += 5

    if subscription_cost > 3000:
        score -= 10

    return max(0, min(score, 100))