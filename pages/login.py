import streamlit as st
from utils.ui import page_header


page_header(
    "Login",
    "Log in to access the bakery demand forecasting system."
)

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username and password:
        st.session_state["logged_in"] = True
        st.success("Login successful!")
    else:
        st.error("Please enter your username and password.")