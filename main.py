import streamlit as st
from datetime import date

st.set_page_config("RC4ME - Login", layout="wide", page_icon="resources/rc4me_logo.png")

import helpers.main as helpers
from helpers import menu, database, auth
from utils import validations

menu.redirect_if_authenticated()
menu.display_menu()

st.title("RC4ME - Login")
helpers.initialise_session_states()

# st.json(st.session_state, expanded=False)

if st.session_state["user_info"].get("email", None) is None:
    st.session_state["user_info"]["email"] = auth.get_user_email()
st.session_state["is_logged_in"] = st.session_state["user_info"]["email"] is not None

if not st.session_state["is_logged_in"]:
    auth.display_login_button()
    st.stop()

if st.session_state["is_registered_user"] is None:
    with st.spinner("Verifying account..."):
        st.session_state["is_registered_user"] = database.is_registered_user(
            st.session_state["user_info"]["email"]
        )

if not st.session_state["is_registered_user"]:
    st.header("Hi, looks like it's your first time here!")
    st.subheader("Just key in a few details for us:")
    name = st.text_input("Full name (as in matriculation card)")
    student_id = st.text_input("Student ID (eg. `E1234567`)")
    tele_handle = st.text_input("Telegram handle")
    phone_number = st.text_input("Contact number")
    room_number = st.selectbox(
        "Room number",
        placeholder="Enter room number",
        options=helpers.get_room_numbers(),
        index=None,
    )
    grad_year = st.number_input(
        "Year of graduation",
        min_value=date.today().year,
        max_value=date.today().year + 4,
        value=date.today().year + 4,
    )
    if st.button(
        "Register",
        type="primary",
        disabled=not validations.is_valid_student_id(student_id)
        or not validations.is_valid_phone_number(phone_number)
        or tele_handle is None
        or grad_year is None
        or room_number is None,
    ):
        try:
            with st.spinner("Registering..."):
                if database.is_already_registered(student_id, tele_handle, phone_number):
                    raise ValueError(
                        "Your Telegram handle / Student ID / contact number is already registered."
                    )
                database.register_student(
                    student_id,
                    tele_handle,
                    phone_number,
                    st.session_state["user_info"]["email"],
                    name,
                    room_number,
                    grad_year,
                )
            st.session_state["is_registered_user"] = True
            st.session_state["user_info"].update(
                database.get_user_details(st.session_state["user_info"]["email"])
            )
            st.rerun()
        except ValueError as e:
            st.warning(str(e))

if st.session_state["is_registered_user"] and st.session_state["is_logged_in"]:
    st.session_state["user_info"].update(
        database.get_user_details(st.session_state["user_info"]["email"])
    )
    st.switch_page("pages/submit_bookings.py")
