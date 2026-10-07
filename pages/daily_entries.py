import streamlit as st
from datetime import date

from utils.ui import page_header, require_login


require_login()

page_header(
    "Daily Entries",
    "Enter today's production and sales information."
)


# -----------------------------
# Entry Date
# -----------------------------

st.subheader("Daily Entry")

entry_date = st.date_input(
    "Entry Date",
    value=date.today()
)


# -----------------------------
# Product & Prediction Data
# -----------------------------
# Temporary product catalogue and predictions.
# These will later come from the backend/database.
#
# Predicted Demand is intentionally NOT editable.
# It represents the prediction made for this date.

products = [
    {
        "Product": "Croissant",
        "Predicted Demand": 45,
        "Units Produced": 0,
        "Units Sold": 0
    },
    {
        "Product": "Chocolate Cake",
        "Predicted Demand": 18,
        "Units Produced": 0,
        "Units Sold": 0
    },
    {
        "Product": "Chicken Puff",
        "Predicted Demand": 32,
        "Units Produced": 0,
        "Units Sold": 0
    },
    {
        "Product": "Fish Bun",
        "Predicted Demand": 27,
        "Units Produced": 0,
        "Units Sold": 0
    },
]


# -----------------------------
# Production & Sales Table
# -----------------------------

st.write(
    "Enter the number of units produced and sold for each product."
)

edited_data = st.data_editor(
    products,
    column_config={
        "Product": st.column_config.TextColumn(
            "Product",
            disabled=True
        ),
        "Predicted Demand": st.column_config.NumberColumn(
            "Predicted Demand",
            disabled=True,
            format="%d"
        ),
        "Units Produced": st.column_config.NumberColumn(
            "Units Produced",
            min_value=0,
            step=1
        ),
        "Units Sold": st.column_config.NumberColumn(
            "Units Sold",
            min_value=0,
            step=1
        )
    },
    hide_index=True,
    use_container_width=True,
    num_rows="fixed"
)


# -----------------------------
# Weather
# -----------------------------

st.subheader("Weather")

weather_condition = st.selectbox(
    "Weather Condition",
    [
        "Sunny",
        "Partly Cloudy",
        "Cloudy",
        "Rainy",
        "Stormy"
    ]
)


# -----------------------------
# Validate Entries
# -----------------------------

invalid_entries = []

for item in edited_data:

    if item["Units Sold"] > item["Units Produced"]:

        invalid_entries.append(
            item["Product"]
        )


# -----------------------------
# Save Daily Entries
# -----------------------------

if st.button("Save Daily Entries", type="primary"):

    if invalid_entries:

        st.error(
            "Units sold cannot be greater than units produced for: "
            + ", ".join(invalid_entries)
        )

    else:

        st.success(
            "Daily entries recorded successfully!"
        )

        # -----------------------------
        # Entry Summary
        # -----------------------------

        st.subheader("Entry Summary")

        summary_data = []

        for item in edited_data:

            leftover = (
                item["Units Produced"]
                - item["Units Sold"]
            )

            summary_data.append(
                {
                    "Product": item["Product"],
                    "Predicted Demand": item["Predicted Demand"],
                    "Units Produced": item["Units Produced"],
                    "Units Sold": item["Units Sold"],
                    "Leftover": leftover
                }
            )

        st.dataframe(
            summary_data,
            use_container_width=True,
            hide_index=True
        )

        st.write(f"**Date:** {entry_date}")
        st.write(f"**Weather:** {weather_condition}")