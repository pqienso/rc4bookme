import streamlit as st
from typing import Dict
from streamlit_calendar import calendar
from datetime import datetime

st.set_page_config(
    "RC4ME - Admin View", layout="wide", page_icon="resources/rc4me_logo.png"
)

from helpers import menu, database
import helpers.admin_view as helpers

menu.redirect_if_not_admin()
menu.display_menu()


st.title("Admin view - all bookings")
if (
    st.button("Refresh calendar")
    or st.session_state["calendar"]["admin_bookings_cache"] is None
    or st.session_state["at_page"] != "admin_view"
):
    st.session_state["at_page"] = "admin_view"
    st.session_state["notification"] = None
    with st.spinner("Getting bookings..."):
        helpers.update_admin_bookings_cache()

if st.session_state["notification"] is not None:
    st.info(st.session_state["notification"])

calendar_options = helpers.get_calendar_options()
calendar_event: Dict = calendar(
    st.session_state["calendar"]["admin_bookings_cache"], options=calendar_options
)

if calendar_event.get("callback", "") == "eventClick":
    event = calendar_event["eventClick"]["event"]
    booking_uid = event["extendedProps"]["uuid"]
    booking = database.get_booking_by_uid(booking_uid)
    booking["start"] = (
        booking["booking_start_date"] + " " + booking["booking_start_time"]
    )
    booking["end"] = booking["booking_end_date"] + " " + booking["booking_end_time"]
    start = datetime.fromisoformat(event["start"])
    end = datetime.fromisoformat(event["end"])

    st.subheader(event["title"])
    st.dataframe(
        booking[
            [
                "start",
                "end",
                "name",
                "student_id",
                "phone_number",
                "friend_ids",
                "tele_handle",
                "booking_description",
                "status",
            ]
        ],
        use_container_width=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    try:
        with col1:
            if st.button(
                "Mark as approved", type="primary", disabled=booking["status"] == "A"
            ):
                with st.spinner("Approving booking..."):
                    database.edit_booking_status(booking_uid, "A")
                    helpers.update_admin_bookings_cache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} approved!"
                )
                st.rerun()
        with col2:
            if st.button("Mark as pending", disabled=booking["status"] == "P"):
                with st.spinner("Marking booking as pending..."):
                    database.edit_booking_status(booking_uid, "P")
                    helpers.update_admin_bookings_cache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} marked as pending."
                )
                st.rerun()
        with col3:
            if st.button("Mark as rejected", disabled=booking["status"] == "R"):
                with st.spinner("Rejecting booking..."):
                    database.edit_booking_status(booking_uid, "R")
                    helpers.update_admin_bookings_cache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} rejected."
                )
                st.rerun()
        with col4:
            if st.button("Delete booking"):
                with st.spinner("Deleting booking..."):
                    database.delete_booking(booking_uid)
                    helpers.update_admin_bookings_cache()
                st.session_state["notification"] = (
                    f"Booking by {booking['name']} on {start.strftime('%c')} deleted."
                )
                st.rerun()
    except KeyError as e:
        st.error(str(e))
else:
    st.markdown("Click on any booking to view actions.")
