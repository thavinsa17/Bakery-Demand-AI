import streamlit as st
import pandas as pd
import plotly.express as px

from utils.ui import page_header, require_login


require_login()

page_header(
    "Tomorrow's Demand Forecast",
    "View tomorrow's predicted demand and monitor model performance."
)


# ============================================================
# TEMPORARY DATA
# ============================================================
# These values are only for frontend development.
# They will later be replaced with real data from the backend/ML model.


# -----------------------------
# Tomorrow's Forecast
# -----------------------------

forecast_data = [
    {
        "Product": "Croissant",
        "Predicted Demand": 45
    },
    {
        "Product": "Chocolate Cake",
        "Predicted Demand": 18
    },
    {
        "Product": "Chicken Puff",
        "Predicted Demand": 32
    },
    {
        "Product": "Fish Bun",
        "Predicted Demand": 27
    },
]


# -----------------------------
# Historical Model Performance
# -----------------------------
# Temporary example data for frontend testing.

performance_data = [
    {"Date": "Oct 1", "Product": "Croissant", "Actual": 47, "Predicted": 45},
    {"Date": "Oct 2", "Product": "Croissant", "Actual": 50, "Predicted": 52},
    {"Date": "Oct 3", "Product": "Croissant", "Actual": 51, "Predicted": 48},
    {"Date": "Oct 4", "Product": "Croissant", "Actual": 44, "Predicted": 46},

    {"Date": "Oct 1", "Product": "Chocolate Cake", "Actual": 20, "Predicted": 18},
    {"Date": "Oct 2", "Product": "Chocolate Cake", "Actual": 17, "Predicted": 19},
    {"Date": "Oct 3", "Product": "Chocolate Cake", "Actual": 21, "Predicted": 20},
    {"Date": "Oct 4", "Product": "Chocolate Cake", "Actual": 18, "Predicted": 17},

    {"Date": "Oct 1", "Product": "Chicken Puff", "Actual": 34, "Predicted": 32},
    {"Date": "Oct 2", "Product": "Chicken Puff", "Actual": 31, "Predicted": 33},
    {"Date": "Oct 3", "Product": "Chicken Puff", "Actual": 36, "Predicted": 35},
    {"Date": "Oct 4", "Product": "Chicken Puff", "Actual": 29, "Predicted": 31},

    {"Date": "Oct 1", "Product": "Fish Bun", "Actual": 25, "Predicted": 27},
    {"Date": "Oct 2", "Product": "Fish Bun", "Actual": 29, "Predicted": 28},
    {"Date": "Oct 3", "Product": "Fish Bun", "Actual": 26, "Predicted": 24},
    {"Date": "Oct 4", "Product": "Fish Bun", "Actual": 28, "Predicted": 27},
]


performance_df = pd.DataFrame(performance_data)


# ============================================================
# TOMORROW'S FORECAST
# ============================================================

st.subheader("Tomorrow's Forecast")

forecast_df = pd.DataFrame(forecast_data)

st.dataframe(
    forecast_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MODEL PERFORMANCE
# ============================================================

st.subheader("Model Performance")


# Calculate temporary metrics
mae = (
    performance_df["Actual"]
    - performance_df["Predicted"]
).abs().mean()

rmse = (
    (
        performance_df["Actual"]
        - performance_df["Predicted"]
    ) ** 2
).mean() ** 0.5


# Simple temporary accuracy calculation
accuracy = (
    1
    - (
        (
            performance_df["Actual"]
            - performance_df["Predicted"]
        ).abs()
        / performance_df["Actual"]
    ).mean()
) * 100


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Accuracy",
        f"{accuracy:.1f}%"
    )

with col2:
    st.metric(
        "Mean Absolute Error",
        f"{mae:.1f} units"
    )

with col3:
    st.metric(
        "RMSE",
        f"{rmse:.1f} units"
    )


# ============================================================
# ACTUAL VS PREDICTED
# ============================================================

st.subheader("Actual vs Predicted Demand")

selected_product = st.selectbox(
    "Select Product",
    performance_df["Product"].unique()
)

product_df = performance_df[
    performance_df["Product"] == selected_product
]

chart_df = product_df.melt(
    id_vars=["Date"],
    value_vars=["Actual", "Predicted"],
    var_name="Type",
    value_name="Demand"
)

fig = px.line(
    chart_df,
    x="Date",
    y="Demand",
    color="Type",
    markers=True,
    title=f"{selected_product} Demand"
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Units",
    legend_title="",
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# DEMAND INSIGHTS
# ============================================================

st.subheader("Demand Insights")


average_daily_demand = performance_df.groupby(
    "Date"
)["Actual"].sum().mean()

average_product_demand = performance_df.groupby(
    "Product"
)["Actual"].mean()

highest_demand_product = (
    average_product_demand.idxmax()
)

highest_demand_value = (
    average_product_demand.max()
)


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Daily Demand",
        f"{average_daily_demand:.0f} units"
    )

with col2:
    st.metric(
        "Highest Demand Product",
        highest_demand_product
    )

with col3:
    st.metric(
        "Average Demand",
        f"{highest_demand_value:.0f} units"
    )


# ============================================================
# AVERAGE DEMAND BY PRODUCT
# ============================================================

st.subheader("Average Demand by Product")

average_demand_df = (
    performance_df
    .groupby("Product", as_index=False)["Actual"]
    .mean()
    .rename(
        columns={
            "Actual": "Average Demand"
        }
    )
)

st.dataframe(
    average_demand_df,
    use_container_width=True,
    hide_index=True
)