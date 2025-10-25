import streamlit as st
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import pandas as pd

from helpers import database


# @st.cache_data(spinner=false)
def get_calendar_options() -> Dict:
    with open("resources/all_bookings_calendar_options.json") as file:
        options = json.load(file)
    return options


@st.cache_data(ttl=timedelta(minutes=1), show_spinner=False)
def get_all_users() -> Dict[str, str]:
    df: pd.DataFrame = st.session_state["db"]["users"]
    users_df = pd.DataFrame()
    users_df["description"] = df["name"] + " (E***" + df["student_id"].str[4:] + ")"
    users_df["student_id"] = df["student_id"].copy()
    users_dict = users_df.set_index("description", drop=True)["student_id"].to_dict()

    user_info = st.session_state["user_info"]
    self_name = user_info["name"]
    self_student_id = user_info["student_id"]
    del users_dict[self_name + " (E***" + self_student_id[4:] + ")"]
    return users_dict


def try_insert_booking(
    start_ts: datetime,
    end_ts: datetime,
    student_id: str,
    tele_handle: str,
    phone_number: str,
    name: str,
    event: Optional[str] = "Regular booking",
    friend_ids: Optional[List[str]] = [],
):
    if database.time_slot_is_taken(start_ts, end_ts):
        raise ValueError("Time slot has already been taken")
    database.add_booking(
        name,
        start_ts,
        end_ts,
        student_id,
        tele_handle,
        phone_number,
        booking_description=event,
        friend_ids=friend_ids,
    )


def get_bookings_for_calendar() -> List[Dict]:
    df = database.get_pending_and_approved_bookings()
    if len(df) == 0:
        return []

    student_id = st.session_state["user_info"]["student_id"]
    new_df = pd.DataFrame()
    new_df["start"] = df["start_unix_ms"]
    new_df["end"] = df["end_unix_ms"]
    new_df["title"] = df.apply(
        lambda row: (
            (row["booking_description"] if row["status"] == "A" else "Pending booking")
            + " - booked by "
            + row["name"]
            + " (@"
            + row["tele_handle"]
            + ")"
        ),
        axis=1,
    )
    new_df["color"] = df.apply(
        lambda row: (
            ("green" if row["status"] == "A" else "#8B8000")
            if (row["student_id"] == student_id or student_id in row["friend_ids"])
            else ("#2E8D87" if row["status"] == "A" else "gray")
        ), 
        axis=1,
    )
    return new_df.to_dict(orient="records")


def update_all_bookings_cache():
    st.session_state["calendar"]["all_bookings_cache"] = get_bookings_for_calendar()
