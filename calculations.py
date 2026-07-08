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