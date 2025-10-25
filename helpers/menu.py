import streamlit as st


def redirect_if_unauthenticated():
    is_authenticated = st.session_state.get(
        "is_logged_in", False
    ) and st.session_state.get("is_registered_user", False)
    if not is_authenticated:
        st.switch_page("main.py")


def redirect_if_authenticated():
    is_authenticated = st.session_state.get(
        "is_logged_in", False
    ) and st.session_state.get("is_registered_user", False)
    if is_authenticated:
        st.switch_page("pages/submit_bookings.py")


def redirect_if_not_admin():
    is_authenticated = st.session_state.get(
        "is_logged_in", False
    ) and st.session_state.get("is_registered_user", False)
    if not is_authenticated:
        st.switch_page("main.py")
        return
    if st.session_state["user_info"]["userType"] != "admin":
        st.switch_page("pages/submit_bookings.py")


def display_menu():
    is_authenticated = st.session_state.get(
        "is_logged_in", False
    ) and st.session_state.get("is_registered_user", False)
    if is_authenticated:
        st.sidebar.header(f'Welcome, {st.session_state["user_info"]["name"]}')
        st.sidebar.page_link("pages/submit_bookings.py", label="Submit bookings")
        st.sidebar.page_link("pages/view_your_bookings.py", label="View your bookings")
        if st.session_state["user_info"]["userType"] == "admin":
            st.sidebar.page_link("pages/admin_view.py", label="Admin view")
    else:
        st.sidebar.page_link("main.py", label="Login")
    st.sidebar.page_link("pages/logout.py", label="Logout")
