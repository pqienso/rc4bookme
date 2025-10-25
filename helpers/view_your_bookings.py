from typing import List, Dict
import pandas as pd
import streamlit as st
import json

from helpers import database


def get_user_bookings_for_calendar(student_id: str) -> List[Dict]:
    df = database.get_bookings_for_user(student_id)
    if len(df) == 0:
        return []

    status_mappings = {
        "A": "Approved",
        "P": "Pending",
        "R": "Rejected",
    }
    colour_mappings = {
        "A": "green",
        "P": "yellow",
        "R": "red",
    }
    new_df = pd.DataFrame()
    new_df["start"] = df["start_unix_ms"]
    new_df["end"] = df["end_unix_ms"]
    new_df["title"] = df.apply(
        lambda row: (
            row["booking_description"]
            + " (Status: "
            + status_mappings[row["status"]]
            + ")"
        )
        if row["student_id"] == student_id
        else (row["booking_description"] + " (Booked by " + row["name"] + ")"),
        axis=1,
    )
    new_df["extendedProps"] = df.apply(lambda row: {"uuid": row.name}, axis=1)
    new_df["color"] = df["status"].replace(colour_mappings)
    return new_df.to_dict(orient="records")


def update_user_bookings_cache(student_id: str):
    st.session_state["calendar"]["user_bookings_cache"] = get_user_bookings_for_calendar(
        student_id
    )


# @st.cache_data(show_spinner = false)
def get_calendar_options() -> Dict:
    with open("resources/user_bookings_calendar_options.json") as file:
        options = json.load(file)
    return options

