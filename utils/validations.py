from datetime import datetime, timedelta
import pytz
import streamlit as st


def is_valid_student_id(student_id: str | None) -> bool:
    if student_id is None or student_id == "":
        return False
    if student_id[0].lower() != "e":
        return False
    if len(student_id) != 8:
        return False
    if not student_id[1:].isnumeric():
        return False
    return True


def is_valid_phone_number(number: str | None) -> bool:
    if number is None:
        return False
    if len(number) < 8:
        return False
    for char in number:
        if not char.isnumeric() and char not in ["-", "+", " "]:
            return False
    return True


def verify_booking_period(start: datetime, end: datetime):
    now = datetime.now(tz=pytz.timezone("Singapore"))
    if start > end:
        raise ValueError("End time cannot be earlier than start time")
    if end - start < timedelta(hours=1):
        raise ValueError("Booking must be at least an hour long")
    if st.session_state["user_info"]["userType"] != "admin":
        if start - now < timedelta(days=1):
            raise ValueError("Please book at least 1 day in advance")
        if start - now > timedelta(weeks=2):
            raise ValueError("Please book at most 2 weeks in advance")
        if end - start > timedelta(hours=4):
            raise ValueError("Booking must be less than 4 hours long")
