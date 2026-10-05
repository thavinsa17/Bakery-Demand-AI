import streamlit as st


def page_header(title, description=None):
    st.title(title)

    if description:
        st.write(description)


def show_success(message):
    st.success(message)


def show_error(message):
    st.error(message)

def require_login():
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in to access this page.")
        st.stop()