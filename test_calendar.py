import streamlit as st
import pandas as pd
from datetime import date
from streamlit_calendar import calendar


st.title("Calendar Test")


if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()


cal = calendar(
    events=[],
    options={
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": ""
        },
        "height":500,
        "dateClick": True,
    },
    key="test_calendar"
)


if cal:

    st.write(cal)

    if cal.get("callback") == "dateClick":

        clicked = cal["dateClick"]["date"]

        st.session_state.selected_date = (
            pd.to_datetime(clicked)
            .tz_convert("Asia/Kolkata")
            .date()
        )


st.write(
    "SELECTED:",
    st.session_state.selected_date
)