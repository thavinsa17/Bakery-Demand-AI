import streamlit as st
import pandas as pd

from utils.ui import page_header, require_login
from backend.forecast import forecast_all_products


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Demand Forecast",
    layout="wide",
)

require_login()

# ============================================================
# PAGE STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
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
    </style>
    """,
    unsafe_allow_html=True,
)

page_header(
    "Demand Forecast",
    "Plan tomorrow's production using AI-powered demand predictions.",
)

st.divider()


# ============================================================
# GENERATE FORECAST
# ============================================================

if "forecast_results" not in st.session_state:
    st.session_state["forecast_results"] = None

if st.button("Refresh Forecast", type="primary"):
    st.session_state["forecast_results"] = None

    try:
        with st.spinner("Generating demand forecasts..."):
            st.session_state["forecast_results"] = forecast_all_products()

    except Exception as error:
        st.error("Unable to generate the demand forecast.")

        with st.expander("View error details"):
            st.exception(error)


# Generate the initial forecast when the page is first opened.
if st.session_state["forecast_results"] is None:
    try:
        with st.spinner("Generating demand forecasts..."):
            st.session_state["forecast_results"] = forecast_all_products()

    except Exception as error:
        st.error("Unable to generate the demand forecast.")

        with st.expander("View error details"):
            st.exception(error)

        st.stop()


forecasts = st.session_state["forecast_results"]


# ============================================================
# CHECK FORECAST DATA
# ============================================================

if not forecasts:
    st.warning("No forecast data is currently available.")
    st.stop()

forecast_df = pd.DataFrame(forecasts)

required_columns = [
    "Date",
    "Product",
    "Predicted_Demand",
    "Weather_Condition",
    "Temperature_C",
    "Rainfall_mm",
    "Is_Holiday",
    "Holiday_Name",
]

missing_columns = [
    column
    for column in required_columns
    if column not in forecast_df.columns
]

if missing_columns:
    st.error(
        "The forecast data is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

forecast_df["Date"] = pd.to_datetime(
    forecast_df["Date"],
    errors="coerce",
)

forecast_df["Predicted_Demand"] = pd.to_numeric(
    forecast_df["Predicted_Demand"],
    errors="coerce",
)

forecast_df = forecast_df.dropna(
    subset=["Date", "Product", "Predicted_Demand"]
)

if forecast_df.empty:
    st.warning("No valid forecast records are available.")
    st.stop()

# Demand cannot be negative.
forecast_df["Predicted_Demand"] = (
    forecast_df["Predicted_Demand"].clip(lower=0)
)


# ============================================================
# FORECAST SUMMARY
# ============================================================

forecast_date = pd.to_datetime(
    forecast_df["Date"].iloc[0]
).strftime("%d %B %Y")

total_demand = forecast_df["Predicted_Demand"].sum()
product_count = forecast_df["Product"].nunique()

st.markdown("### Forecast Overview")

date_col, demand_col, products_col = st.columns(3)

with date_col:
    st.metric(
        "Forecast Date",
        forecast_date,
    )

with demand_col:
    st.metric(
        "Total Predicted Units",
        f"{total_demand:,.0f}",
    )

with products_col:
    st.metric(
        "Products Forecast",
        product_count,
    )

st.caption(
    "Total predicted units are the sum of the model's predictions "
    "for all listed products."
)

st.divider()


# ============================================================
# WEATHER AND HOLIDAY INFORMATION
# ============================================================

st.markdown("### Conditions for the Forecast Date")

weather_condition = forecast_df["Weather_Condition"].iloc[0]
temperature = forecast_df["Temperature_C"].iloc[0]
rainfall = forecast_df["Rainfall_mm"].iloc[0]

is_holiday = forecast_df["Is_Holiday"].iloc[0]
holiday_name = forecast_df["Holiday_Name"].iloc[0]

weather_col, temperature_col, rainfall_col = st.columns(3)

with weather_col:
    st.markdown("**Weather**")
    st.markdown(f"### {weather_condition}")

with temperature_col:
    st.markdown("**Temperature**")
    st.markdown(f"### {temperature:.1f} °C")

with rainfall_col:
    st.markdown("**Expected Rainfall**")
    st.markdown(f"### {rainfall:.1f} mm")

if pd.notna(is_holiday) and bool(is_holiday):
    st.info(f"Public holiday: {holiday_name}")
else:
    st.success("No public holiday is expected for this date.")

st.divider()


# ============================================================
# PREPARE PRODUCT DEMAND DATA
# ============================================================

chart_df = (
    forecast_df.groupby(
        "Product",
        as_index=False,
    )["Predicted_Demand"]
    .sum()
    .sort_values(
        "Predicted_Demand",
        ascending=False,
    )
)

chart_df = chart_df.rename(
    columns={
        "Product": "Bakery Product",
        "Predicted_Demand": "Predicted Units",
    }
)

display_df = chart_df.copy()

display_df["Predicted Units"] = (
    display_df["Predicted Units"]
    .round()
    .astype(int)
)


# ============================================================
# PRODUCT DEMAND TABLE
# ============================================================

st.markdown("### Predicted Demand by Product")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Bakery Product": st.column_config.TextColumn(
            "Bakery Product",
        ),
        "Predicted Units": st.column_config.NumberColumn(
            "Predicted Units",
            format="%d",
        ),
    },
)

st.caption(
    "Products are ordered from highest to lowest predicted demand. "
    "Predictions are estimates, so use them alongside your bakery's "
    "experience and actual sales."
)

st.divider()


# ============================================================
# PREDICTED DEMAND BAR CHART
# ============================================================

st.markdown("### Demand Distribution by Product")

st.bar_chart(
    chart_df,
    x="Bakery Product",
    y="Predicted Units",
    horizontal=True,
)

st.caption(
    "Compare predicted demand across products to help plan production "
    "quantities for the forecast date."
)