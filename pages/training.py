import streamlit as st

from utils.ui import page_header, require_login


require_login()

page_header(
    "Model Management",
    "View the current forecasting model and manage model training."
)


# -----------------------------
# Current Model
# -----------------------------

st.subheader("Current Model")

st.write("**Last trained:** 04/10/2026")
st.write("**Training records:** 7,450")
st.write("**Model:** XGBoost")


# -----------------------------
# Retrain Model
# -----------------------------

if st.button("Retrain Model", type="primary"):

    st.info(
        "Model retraining will be connected to the training pipeline later."
    )