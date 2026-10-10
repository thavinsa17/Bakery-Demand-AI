import streamlit as st

st.set_page_config(
    page_title="Bakery Demand AI",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        letter-spacing: -0.5px;
    }

    div.stButton > button {
        border-radius: 8px;
        min-height: 44px;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5D7C7;
        padding: 18px;
        border-radius: 12px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #EDE3D5;
        border-right: 1px solid #E0D0BE;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #49352B;
    }

    /* Navigation links */
    section[data-testid="stSidebar"] a {
        border-radius: 8px;
    }

    /* Main headings */
    h1, h2, h3 {
        color: #49352B;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 8px;
        min-height: 44px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #A95137;
        color: #A95137;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Bakery Demand AI")

st.markdown(
    "### Smarter production. Less waste. Better decisions."
)

st.write(
    "Forecast bakery demand, plan daily production, "
    "track sales, and make informed decisions using "
    "machine learning."
)

st.divider()

if st.session_state.get("logged_in", False):
    name = st.session_state.get("user_name", "there")
    st.success(f"Welcome, {name}!")

    st.subheader("Your bakery workspace")
    st.write(
        "Use the sidebar to access demand forecasts, "
        "daily production entries, bakery profile, "
        "and model management."
    )

    if st.button("Log Out", type="secondary"):
        st.session_state["logged_in"] = False
        st.session_state.pop("user_email", None)
        st.session_state.pop("user_name", None)
        st.rerun()

else:
    st.subheader("Get started")

    st.write(
        "Sign in to your bakery account or create "
        "the first account to get started."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Sign In",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page("pages/login.py")

    with col2:
        if st.button(
            "Create Account",
            use_container_width=True,
        ):
            st.switch_page("pages/login.py")