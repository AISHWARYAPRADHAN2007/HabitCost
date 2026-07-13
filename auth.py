import streamlit as st
from database import supabase


def signup(email, password):

    try:
        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password
            }
        )

        return response

    except Exception as e:
        st.error(e)


def login(email, password):

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )

        return response

    except Exception as e:
        st.error(e)
        return None

def logout():

    supabase.auth.sign_out()

    st.session_state.user = None

def get_user():

    session = supabase.auth.get_session()

    if session:

        return session.user

    return None
def reset_password(email):
    try:
        supabase.auth.reset_password_email(
            email,
            {
                "redirect_to": "https://habitcost.streamlit.app"
            }
        )
        return True, "Password reset email sent!"
    
    except Exception as e:
        return False, str(e)