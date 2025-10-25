import streamlit as st
import pandas as pd
import json
from typing import List, Dict

from helpers import database


def get_admin_bookings() -> List[Dict]:
    database.refresh_bookings()
    df: pd.DataFrame = st.session_state["db"]["bookings"]
    new_df = pd.DataFrame()
    colour_mappings = {
        "A": "green",
        "P": "#8B8000",
        "R": "red",
    }
    new_df["title"] = (
        df["booking_description"] + " - " + df["name"] + " (@" + df["tele_handle"] + ")"
    )
    new_df["color"] = df["status"].replace(colour_mappings)
    new_df["start"] = df["start_unix_ms"]
    new_df["end"] = df["end_unix_ms"]
    new_df["extendedProps"] = df.apply(
        lambda row: {"uuid": row.name},
        axis=1,
    )
    return new_df.to_dict(orient="records")


def update_admin_bookings_cache():
    st.session_state["calendar"]["admin_bookings_cache"] = get_admin_bookings()


def get_calendar_options() -> Dict:
    with open("resources/all_bookings_calendar_options.json") as file:
        options = json.load(file)
    return options
