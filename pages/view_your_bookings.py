import streamlit as st
from streamlit_calendar import calendar
import pytz
from datetime import timedelta, datetime

st.set_page_config(
    "RC4ME - View Bookings", layout="wide", page_icon="resources/rc4me_logo.png"
)

import helpers.view_your_bookings as helpers
from helpers import menu, database
from utils import validations

menu.redirect_if_unauthenticated()
menu.display_menu()

calendars_state = st.session_state["calendar"]
student_id = st.session_state["user_info"]["student_id"]

st.title("View bookings")
# st.json(st.session_state, expanded=False)
if (
    st.session_state["calendar"]["user_bookings_cache"] is None
    or st.button("Refresh calendar")
    or st.session_state["at_page"] != "view_your_bookings"
):
    st.session_state["notification"] = None
    st.session_state["at_page"] = "view_your_bookings"
    with st.spinner("Getting bookings..."):
        helpers.update_user_bookings_cache(student_id)

if st.session_state["notification"] is not None:
    st.info(st.session_state["notification"])

calendar_options = helpers.get_calendar_options()
calendar_event = calendar(
    st.session_state["calendar"]["user_bookings_cache"], options=calendar_options
)


pending_event_clicked = False
if calendar_event.get("callback", "") == "eventClick":
    booking_uid = calendar_event["eventClick"]["event"]["extendedProps"]["uuid"]
    try:
        booking = database.get_booking_by_uid(booking_uid)
    except KeyError:
        booking = {"status": ""}
    if booking["status"] == "P":
        pending_event_clicked = True
        is_admin = st.session_state["user_info"]["userType"] == "admin"
        old_start_ts = datetime.fromtimestamp(
            booking["start_unix_ms"] / 1000, tz=pytz.timezone("Singapore")
        )
        old_end_ts = datetime.fromtimestamp(
            booking["end_unix_ms"] / 1000, tz=pytz.timezone("Singapore")
        )

        st.subheader(f"Edit / cancel booking on {old_start_ts.strftime("%c")}")
        old_duration = old_end_ts - old_start_ts
        today = datetime.now(pytz.timezone("Singapore")).date()

        new_start_date = st.date_input(
            "### Start date",
            value=old_start_ts.date(),
            min_value=None if is_admin else today,
            max_value=None if is_admin else today + timedelta(weeks=2),
        )
        new_start_time = st.time_input(
            "### Start time", step=timedelta(hours=0.5), value=old_start_ts.time()
        )
        new_start_ts = pytz.timezone("Singapore").localize(
            datetime.combine(new_start_date, new_start_time)
        )

        default_end_ts = new_start_ts + old_duration
        new_end_date = st.date_input(
            "### End date",
            min_value=new_start_date,
            value=default_end_ts.date(),
        )
        new_end_time = st.time_input(
            "### End time",
            step=timedelta(hours=0.5),
            value=default_end_ts.time(),
        )
        new_end_ts = pytz.timezone("Singapore").localize(
            datetime.combine(new_end_date, new_end_time)
        )

        has_edited_booking = new_end_ts != old_end_ts or new_start_ts != old_start_ts
        if st.button("Edit booking", type="primary", disabled=not has_edited_booking):
            try:
                with st.spinner("Editing booking..."):
                    validations.verify_booking_period(new_start_ts, new_end_ts)
                    if database.time_slot_is_taken(new_start_ts, new_end_ts):
                        raise ValueError("Time slot has already been taken")
                    database.edit_booking_timing(booking_uid, new_start_ts, new_end_ts)
                    helpers.update_user_bookings_cache(student_id)
                st.session_state["notification"] = (
                    f"Booking on {old_start_ts.date().isoformat()} edited!"
                )
                st.rerun()
            except (ValueError, KeyError) as e:
                st.error(str(e))
        if st.button("Cancel booking", type="primary"):
            try:
                with st.spinner("Cancelling booking..."):
                    database.delete_booking(booking_uid)
                    helpers.update_user_bookings_cache(student_id)
                st.session_state["notification"] = (
                    f"Booking on {old_start_ts.date().isoformat()} cancelled."
                )
                st.rerun()
            except KeyError as e:
                st.error(str(e))

if not pending_event_clicked:
    st.markdown("Click on any pending bookings to edit or cancel them.")
