from supabase import create_client
from datetime import date
import pandas as pd

import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

def get_habits(email):

    response = (
        supabase
        .table("habits")
        .select("*")
        .eq("user_email", email)
        .execute()
    )

    return response.data


def add_habit(email, habit):

    return supabase.table("habits").insert({

        "user_email": email,
        "habit": habit["Habit"],
        "category": habit["Category"],
        "cost": habit["Cost"],
        "frequency": habit["Frequency"],
        "tracking_type": habit["Tracking_Type"],
        "billing_day": habit["Billing_Day"],
        "start_date": str(date.today()),

    }).execute()



def delete_habit(user_email, habit_id):

    return (
        supabase
        .table("habits")
        .delete()
        .eq("id", habit_id)
        .eq("user_email", user_email)
        .execute()
    )
def update_habit(user_email, habit_id, habit):

    billing_day = habit.get("Billing_Day")

    if pd.isna(billing_day):
        billing_day = None
    else:
        billing_day = int(billing_day)

    return (
        supabase
        .table("habits")
        .update({
            "habit": habit["Habit"],
            "category": habit["Category"],
            "cost": float(habit["Cost"]) if habit["Cost"] is not None else 0,
            "frequency": habit["Frequency"],
            "tracking_type": habit.get("Tracking_Type"),
            "billing_day": billing_day,
        })
        .eq("id", habit_id)
        .eq("user_email", user_email)
        .execute()
    )
def get_profile(email):

    response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("email", email)
        .execute()
    )

    if response.data:
        return response.data[0]

    return {}


def save_profile(email, income, currency,  investment_rate, monthly_budget, goal, notes,):

    profile = {
        "email": email,
        "income": income,
        "currency": currency,
        "investment_rate": investment_rate,
        "monthly_budget": monthly_budget,
        "goal": goal,
        "notes": notes,
        
    }

    response = (
        supabase
        .table("profiles")
        .upsert(profile)
        .execute()
    )

    return response.data

def add_habit_history(
    email,
    month,
    habit,
    category,
    monthly_cost
):

    return (
        supabase
        .table("habit_history")
        .insert({
            "user_email": email,
            "month": month,
            "habit": habit,
            "category": category,
            "monthly_cost": monthly_cost,
        })
        .execute()
    )

def get_habit_history(email):

    response = (
        supabase
        .table("habit_history")
        .select("*")
        .eq("user_email", email)
        .execute()
    )

    return response.data


def add_month_snapshot(
    email,
    month,
    spending,
    top_category,
    habits
):

    return (
        supabase
        .table("monthly_snapshots")
        .insert({
            "user_email": email,
            "month": month,
            "spending": spending,
            "top_category": top_category,
            "habits": habits,
        })
        .execute()
    )


def get_month_snapshots(email):

    response = (
        supabase
        .table("monthly_snapshots")
        .select("*")
        .eq("user_email", email)
        .order("created_at")
        .execute()
    )

    return response.data

def add_habit_log(user_email, habit_id, log_date, completed,amount):

    return (
        supabase
        .table("habit_logs")
        .upsert(
            {
                "user_email": user_email,
                "habit_id": habit_id,
                "log_date": log_date.isoformat(),
                "completed": completed,
                "amount": amount
            },
            on_conflict="habit_id,log_date"
        )
        .execute()
    )



def get_habit_logs(user_email, log_date):

    response = (
        supabase
        .table("habit_logs")
        .select("*")
        .eq("user_email", user_email)
        .eq("log_date", log_date.isoformat())
        .execute()
    )

    return response.data

def get_budget(email):

    response = (
        supabase
        .table("profiles")
        .select("monthly_budget")
        .eq("email", email)
        .execute()
    )

    if response.data:

        budget = response.data[0]["monthly_budget"]

        if budget is None:
            return 0

        return budget

    return 0



def save_budget(email, budget):

    return (
        supabase
        .table("profiles")
        .update({
            "monthly_budget": budget
        })
        .eq("email", email)
        .execute()
    )
def get_all_habit_logs(email):

    response = (
        supabase
        .table("habit_logs")
        .select("*")
        .eq("user_email", email)
        .execute()
    )

    return response.data

def get_saved_achievements(email):

    try:

        response = (
            supabase
            .table("achievements")
            .select("*")
            .eq("user_email", email)
            .execute()
        )

        return response.data

    except Exception as e:

        print("GET ACHIEVEMENTS ERROR:", e)

        return []


def save_achievement(email, name):

    try:

        return (
            supabase
            .table("achievements")
            .insert(
                {
                    "user_email": email,
                    "achievement_name": name
                }
            )
            .execute()
        )

    except Exception as e:

        print("SAVE ACHIEVEMENT ERROR:", e)

        return None