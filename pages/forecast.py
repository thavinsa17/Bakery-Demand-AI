import streamlit as st
import pandas as pd

from utils.ui import page_header, require_login
from backend.forecast import forecast_all_products


# ============================================================
# PAGE SETUP
# ============================================================

require_login()

page_header(
    "Tomorrow's Demand Forecast",
    "View the predicted demand for each bakery product."
)


# ============================================================
# LOAD FORECAST
# ============================================================

try:
    forecasts = forecast_all_products()

except Exception as error:
    st.error(
        "Unable to generate the demand forecast."
    )

    st.exception(error)

    st.stop()


# ============================================================
# CHECK FORECAST
# ============================================================

if not forecasts:

    st.warning(
        "No forecast data is currently available."
    )

    st.stop()


# Convert the forecast list into a DataFrame
forecast_df = pd.DataFrame(forecasts)


# ============================================================
# TOMORROW'S FORECAST
# ============================================================

st.subheader("Tomorrow's Forecast")


# Keep only the information needed for the main table
display_df = forecast_df[
    [
        "Product",
        "Predicted_Demand"
    ]
].copy()


# Rename columns for a cleaner display
display_df = display_df.rename(
    columns={
        "Predicted_Demand": "Predicted Demand"
    }
)


# Display forecast table
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FORECAST INFORMATION
# ============================================================

st.subheader("Forecast Information")

forecast_date = forecast_df["Date"].iloc[0]

st.write(
    f"**Forecast Date:** {forecast_date}"
)


# ============================================================
# WEATHER INFORMATION
# ============================================================

weather_condition = forecast_df[
    "Weather_Condition"
].iloc[0]

temperature = forecast_df[
    "Temperature_C"
].iloc[0]

rainfall = forecast_df[
    "Rainfall_mm"
].iloc[0]


st.write(
    f"**Weather:** {weather_condition}"
)

st.write(
    f"**Temperature:** {temperature:.1f} °C"
)

st.write(
    f"**Expected Rainfall:** {rainfall:.1f} mm"
)


# ============================================================
# HOLIDAY INFORMATION
# ============================================================

is_holiday = forecast_df[
    "Is_Holiday"
].iloc[0]

holiday_name = forecast_df[
    "Holiday_Name"
].iloc[0]


if is_holiday:

    st.info(
        f"Tomorrow is a holiday: {holiday_name}"
    )

else:

    st.write(
        "**Holiday:** No holiday"
    )