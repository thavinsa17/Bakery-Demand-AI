import streamlit as st

st.set_page_config(
    page_title="Bakery Demand AI",
    page_icon="🥐",
    layout="wide",
)

st.title("🥐 Bakery Demand AI")

st.write(
    "AI-powered demand forecasting to help bakeries plan "
    "production, reduce leftovers, and understand demand."
)

if st.session_state.get("logged_in", False):
    name = st.session_state.get("user_name", "there")

    st.success(f"Welcome, {name}!")

    st.info(
        "Use the sidebar to access Forecast, Daily Entries, "
        "Bakery Profile, and Model Management."
    )

    if st.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state.pop("user_email", None)
        st.session_state.pop("user_name", None)
        st.rerun()

else:
    st.write("Get started by signing in or creating your account.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sign In", type="primary", use_container_width=True):
            st.switch_page("pages/login.py")

    with col2:
        if st.button("Create Account", use_container_width=True):
            st.switch_page("pages/login.py")
