import streamlit as st
import pandas as pd
from datetime import date

from utils.ui import page_header, require_login
from backend.data import (
    get_products,
    load_bakery_data,
    validate_daily_entry,
    add_daily_entry,
    calculate_leftover,
    get_forecast_data,
)
from backend.weather import get_today_weather
from backend.holidays import get_holiday_info


st.set_page_config(
    page_title="Daily Entries",
    page_icon="🥐",
    layout="wide",
)

require_login()

page_header(
    "Daily Entries",
    "Record today's production and sales information."
)

entry_date = st.date_input(
    "Entry Date",
    value=date.today(),
    max_value=date.today(),
)

if entry_date != date.today():
    st.info("Daily Entries currently supports recording today's actual production and sales.")
    st.stop()


# ------------------------------------------------------------
# LOAD WEATHER AND HOLIDAY INFORMATION
# ------------------------------------------------------------

try:
    weather_data = get_today_weather()
    holiday_data = get_holiday_info(entry_date)
except Exception as error:
    st.error(f"Could not load today's weather or holiday information: {error}")
    st.stop()


# ------------------------------------------------------------
# DISPLAY TODAY'S CONDITIONS
# ------------------------------------------------------------

st.subheader("Today's Conditions")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Temperature",
    f"{weather_data['Temperature_C']} °C"
)

col2.metric(
    "Rainfall",
    f"{weather_data['Rainfall_mm']} mm"
)

col3.metric(
    "Weather",
    weather_data["Weather_Condition"]
)

if holiday_data["Is_Holiday"]:
    st.info(f"Today is a holiday: {holiday_data['Holiday_Name']}")
else:
    st.write("Today is not a public holiday.")

st.divider()


# ------------------------------------------------------------
# LOAD PRODUCTS AND SAVED FORECASTS
# ------------------------------------------------------------

st.subheader("Production and Sales")

try:
    products = get_products()

    if not products:
        st.error("No products were found in the bakery data.")
        st.stop()

    forecast_data = get_forecast_data(entry_date)

    forecast_lookup = dict(
        zip(
            forecast_data["Product"],
            forecast_data["Predicted_Demand"],
        )
    )

except Exception as error:
    st.error(f"Could not load products or saved forecasts: {error}")
    st.stop()


# ------------------------------------------------------------
# CHECK EXISTING ENTRIES
# ------------------------------------------------------------

try:
    existing_data = load_bakery_data()

    existing_data["Date"] = pd.to_datetime(
        existing_data["Date"],
        errors="coerce",
    ).dt.date

    existing_today = existing_data[
        existing_data["Date"] == entry_date
    ]

except Exception as error:
    st.error(f"Could not check existing daily entries: {error}")
    st.stop()

existing_products = set(
    existing_today["Product"].astype(str)
)

if existing_products:
    st.info(
        "Products already recorded today are excluded to prevent "
        "duplicate entries."
    )

available_products = [
    product
    for product in products
    if product not in existing_products
]

if not available_products:
    st.success("All products already have entries for today.")
    st.stop()


# ------------------------------------------------------------
# FOUR-COLUMN DAILY ENTRY TABLE
# ------------------------------------------------------------

entry_rows = [
    {
        "Product": product,
        "Predicted Units": (
            forecast_lookup.get(product, "-")
        ),
        "Units Produced": 0,
        "Units Sold": 0,
    }
    for product in available_products
]

edited_data = st.data_editor(
    pd.DataFrame(entry_rows),
    hide_index=True,
    use_container_width=True,
    disabled=["Product", "Predicted Units"],
    column_config={
        "Product": st.column_config.TextColumn(
            "Product",
        ),
        "Predicted Units": st.column_config.TextColumn(
            "Predicted Units",
            help=(
                "Forecast previously saved for this date. "
                "A dash means no saved forecast is available."
            ),
        ),
        "Units Produced": st.column_config.NumberColumn(
            "Units Produced",
            min_value=0,
            step=1,
        ),
        "Units Sold": st.column_config.NumberColumn(
            "Units Sold",
            min_value=0,
            step=1,
        ),
    },
)


# ------------------------------------------------------------
# SAVE DAILY ENTRIES
# ------------------------------------------------------------

if st.button("Save Daily Entries", type="primary"):

    errors = []

    # Validate all rows before saving any.
    for _, item in edited_data.iterrows():
        product = item["Product"]
        produced = item["Units Produced"]
        sold = item["Units Sold"]

        if pd.isna(produced) or pd.isna(sold):
            errors.append(
                f"{product}: enter both production and sales quantities."
            )
            continue

        if (
            produced < 0
            or sold < 0
            or float(produced) != int(produced)
            or float(sold) != int(sold)
        ):
            errors.append(
                f"{product}: quantities must be non-negative whole numbers."
            )
            continue

        try:
            validate_daily_entry(
                product,
                int(produced),
                int(sold),
            )
        except (ValueError, TypeError) as error:
            errors.append(f"{product}: {error}")

    # Stop if any row is invalid.
    if errors:
        for error in errors:
            st.error(error)

    else:
        # Recheck the CSV in case entries changed before saving.
        latest_data = load_bakery_data()

        latest_data["Date"] = pd.to_datetime(
            latest_data["Date"],
            errors="coerce",
        ).dt.date

        latest_today = latest_data[
            latest_data["Date"] == entry_date
        ]

        latest_products = set(
            latest_today["Product"].astype(str)
        )

        duplicate_products = [
            product
            for product in edited_data["Product"]
            if product in latest_products
        ]

        if duplicate_products:
            st.error(
                "Entries already exist for: "
                + ", ".join(duplicate_products)
                + ". Please refresh the page before saving."
            )

        else:
            saved_rows = []

            try:
                for _, item in edited_data.iterrows():
                    product = item["Product"]
                    produced = int(item["Units Produced"])
                    sold = int(item["Units Sold"])

                    add_daily_entry(
                        target_date=entry_date,
                        product=product,
                        units_produced=produced,
                        units_sold=sold,
                        weather_data=weather_data,
                        holiday_data=holiday_data,
                    )

                    saved_rows.append({
                        "Product": product,
                        "Units Produced": produced,
                        "Units Sold": sold,
                        "Leftover": calculate_leftover(
                            produced,
                            sold,
                        ),
                    })

                st.success("Daily entries saved successfully!")

                st.subheader("Saved Entry Summary")

                st.dataframe(
                    pd.DataFrame(saved_rows),
                    hide_index=True,
                    use_container_width=True,
                )


            except Exception as error:
                st.error(
                    "An error occurred while saving entries. "
                    "Some entries may already have been saved. "
                    "Check the CSV before retrying. "
                    f"Details: {error}"
                )