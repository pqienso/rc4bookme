import streamlit as st


def redirectIfUnauthenticated():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if not isAuthenticated:
        st.switch_page("main.py")


def redirectIfAuthenticated():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if isAuthenticated:
        st.switch_page("pages/submitBookings.py")


def displayMenu():
    isAuthenticated = st.session_state.get(
        "isLoggedIn", False
    ) and st.session_state.get("isRegisteredUser", False)
    if isAuthenticated:
        name = st.session_state["userInfo"]["name"]
        st.sidebar.header(f"Welcome, {name}")
        st.sidebar.page_link("pages/submitBookings.py", label="Submit bookings")
        st.sidebar.page_link("pages/viewYourBookings.py", label="View your bookings")
    else:
        st.sidebar.page_link("main.py", label="Login")
    st.sidebar.page_link("pages/logout.py", label="Logout")
