import streamlit as st

from utils.ui import page_header, require_login


require_login()

page_header(
    "Model Management",
    "View the current forecasting model and manage model training."
)


st.subheader("Current Model")

st.write("Model status: **Ready**")
st.write("Model type: **Demand Forecasting Model**")


st.subheader("Model Training")

st.write(
    "Retraining the model will use the latest available bakery data."
)

if st.button("Retrain Model"):
    st.info(
        "Model training will be connected to the backend later."
    )