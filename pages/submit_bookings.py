import streamlit as st
from streamlit_calendar import calendar
from datetime import timedelta, datetime
import pytz
from typing import List, Dict

st.set_page_config("RC4ME - Book", layout="wide", page_icon="resources/rc4me_logo.png")

from utils import validations
from helpers import menu
import helpers.submit_bookings as helpers

menu.redirect_if_unauthenticated()
menu.display_menu()

# st.json(st.session_state, expanded=False)

st.header("TR3 availability")
if (
    st.button("Refresh calendar")
    or st.session_state["calendar"]["all_bookings_cache"] is None
    or st.session_state["at_page"] != "submit_bookings"
):
    st.session_state["at_page"] = "submit_bookings"
    with st.spinner("Getting bookings..."):
        helpers.update_all_bookings_cache()

calendar_options = helpers.get_calendar_options()
calendar_event: Dict = calendar(
    st.session_state["calendar"]["all_bookings_cache"], options=calendar_options
)
if calendar_event.get("callback", "") == "eventClick":
    components = calendar_event["eventClick"]["event"]["title"].split("@")
    tele_handle = components[-1][:-1]
    event = "".join(components[:-1])
    st.toast(event + f"[@{tele_handle}](https://t.me/{tele_handle}))")

is_admin = st.session_state["user_info"]["userType"] == "admin"
st.subheader("Submit bookings")
today = datetime.now(pytz.timezone("Singapore")).date()
start_date = st.date_input(
    "### Start date",
    value=today + timedelta(days=2),
    min_value=None if is_admin else today,
    max_value=None if is_admin else today + timedelta(weeks=2),
)
start_time = st.time_input("### Start time", step=timedelta(hours=0.5), value=None)
start_ts = (
    None
    if start_time is None
    else pytz.timezone("Singapore").localize(datetime.combine(start_date, start_time))
)

default_end = None if start_ts is None else start_ts + timedelta(hours=2)
end_date = st.date_input(
    "### End date",
    min_value=start_date,
    value=None if default_end is None else default_end.date(),
)
end_time = st.time_input(
    "### End time",
    step=timedelta(hours=0.5),
    value=None if default_end is None else default_end.time(),
)
end_ts = (
    None
    if (end_date is None or end_time is None)
    else pytz.timezone("Singapore").localize(datetime.combine(end_date, end_time))
)

booking_description = "Regular booking"
if st.session_state["user_info"]["userType"] == "admin":
    booking_description = st.text_input("Booking description", value="Regular booking")

friend_list: List = st.session_state["booking_form"]["friend_ids"]
all_users = helpers.get_all_users()
if st.checkbox("I'm using TR3 with friends!"):
    friends = st.multiselect(
        "Booking used with:", options=all_users, placeholder="Enter names..."
    )
else:
    friends = []
friend_ids = [all_users[friend] for friend in friends]

if st.button("Submit", type="primary", disabled=end_ts is None or start_ts is None):
    try:
        validations.verify_booking_period(start_ts, end_ts)
        with st.spinner("Processing booking..."):
            helpers.try_insert_booking(
                start_ts,
                end_ts,
                st.session_state["user_info"]["student_id"],
                st.session_state["user_info"]["tele_handle"],
                st.session_state["user_info"]["phone_number"],
                st.session_state["user_info"]["name"],
                friend_ids=friend_ids,
                event=booking_description,
            )
        st.info("Booking submitted!")
    except ValueError as e:
        st.error(str(e))
