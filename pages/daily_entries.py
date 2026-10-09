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
)
from backend.weather import get_today_weather
from backend.holidays import get_holiday_info


st.set_page_config(page_title="Daily Entries", page_icon="🥐", layout="wide")

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
    st.info("This page currently records today's entries only. Please select today's date.")
    st.stop()

try:
    weather_data = get_today_weather()
    holiday_data = get_holiday_info(entry_date)
except Exception as error:
    st.error(f"Could not load today's weather or holiday information: {error}")
    st.stop()

st.subheader("Today's Conditions")
col1, col2, col3 = st.columns(3)

col1.metric("Temperature", f"{weather_data['Temperature_C']} °C")
col2.metric("Rainfall", f"{weather_data['Rainfall_mm']} mm")
col3.metric("Weather", weather_data["Weather_Condition"])

if holiday_data["Is_Holiday"]:
    st.info(f"Today is a holiday: {holiday_data['Holiday_Name']}")
else:
    st.write("Today is not a public holiday.")

st.divider()
st.subheader("Production and Sales")

products = get_products()

if not products:
    st.error("No products were found in the bakery data.")
    st.stop()

existing_data = load_bakery_data()
existing_today = existing_data[
    pd.to_datetime(existing_data["Date"]).dt.date == entry_date
]

if not existing_today.empty:
    st.warning(
        "Some entries already exist for today. You can add products "
        "that have not been recorded yet; existing product entries "
        "will not be overwritten."
    )

existing_products = set(existing_today["Product"].astype(str))

available_products = [
    product for product in products if product not in existing_products
]

if not available_products:
    st.success("All products already have entries for today.")
    st.stop()

entry_rows = [
    {
        "Product": product,
        "Units Produced": 0,
        "Units Sold": 0,
    }
    for product in available_products
]

edited_data = st.data_editor(
    pd.DataFrame(entry_rows),
    hide_index=True,
    use_container_width=True,
    disabled=["Product"],
    column_config={
        "Product": st.column_config.TextColumn("Product"),
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

if st.button("Save Daily Entries", type="primary"):
    errors = []

    for _, item in edited_data.iterrows():
        product = item["Product"]
        produced = item["Units Produced"]
        sold = item["Units Sold"]

        if pd.isna(produced) or pd.isna(sold):
            errors.append(f"{product}: enter both production and sales quantities.")
            continue

        if int(produced) != produced or int(sold) != sold:
            errors.append(f"{product}: quantities must be whole numbers.")
            continue

        try:
            validate_daily_entry(product, int(produced), int(sold))
        except (ValueError, TypeError) as error:
            errors.append(f"{product}: {error}")

    if errors:
        for error in errors:
            st.error(error)
        st.stop()

    try:
        saved_rows = []

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
                "Leftover": calculate_leftover(produced, sold),
            })

        st.success("Daily entries saved successfully!")
        st.dataframe(
            pd.DataFrame(saved_rows),
            hide_index=True,
            use_container_width=True,
        )

    except Exception as error:
        st.error(
            "An error occurred while saving entries. Please check the "
            f"CSV before trying again to avoid duplicate entries. Details: {error}"
        )