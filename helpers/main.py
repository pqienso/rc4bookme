import streamlit as st
from typing import List
from utils import states


@st.cache_data()
def get_room_numbers() -> List[str]:
    room_numbers = [
        f"#{level:02}-{suite_number}{suite_unit}"
        for level in range(3, 18)
        for suite_number in ["01", "11", "12"]
        for suite_unit in ["A", "B", "C", "D", "E", "F"]
    ]
    room_numbers += [
        f"#{level:02}-{unit:02}" for level in range(3, 18) for unit in range(2, 11)
    ]
    room_numbers += [
        f"#{level:02}-{unit:02}" for level in range(3, 18) for unit in range(13, 28)
    ]
    return sorted(room_numbers)


def initialise_session_states():
    states.set_state("booking_form", {"friend_ids": []})
    states.set_state(
        "db",
        {"bookings": None, "users": None},
    )
    states.set_state("at_page", "main")
    states.set_state(
        "calendar",
        {
            "all_bookings_cache": None,
            "user_bookings_cache": None,
            "admin_bookings_cache": None,
        },
    )
    states.set_state("notification", None)
    states.set_state("user_info", {})
    states.set_state("is_logged_in", False)
    states.set_state("is_registered_user", None)
