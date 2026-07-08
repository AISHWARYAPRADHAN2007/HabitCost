import math


def months_to_goal(monthly_savings, goal_amount):

    if monthly_savings <= 0:
        return None

    return math.ceil(goal_amount / monthly_savings)