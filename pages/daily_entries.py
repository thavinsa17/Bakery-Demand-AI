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
    page_title="Daily Production & Sales",
    layout="wide",
)

require_login()

page_header(
    "Daily Production & Sales",
    "Record actual production and sales to track bakery performance.",
)

st.divider()

entry_date = date.today()

# Conditions
try:
    weather_data = get_today_weather()
    holiday_data = get_holiday_info(entry_date)
except Exception as error:
    st.error(f"Unable to load today's conditions: {error}")
    st.stop()

st.markdown("### Today's Conditions")

weather_col, temp_col, rain_col = st.columns(3)

with weather_col:
    st.markdown("**Weather**")
    st.markdown(f"### {weather_data['Weather_Condition']}")

with temp_col:
    st.markdown("**Temperature**")
    st.markdown(f"### {weather_data['Temperature_C']:.1f} °C")

with rain_col:
    st.markdown("**Rainfall**")
    st.markdown(f"### {weather_data['Rainfall_mm']:.1f} mm")

if holiday_data["Is_Holiday"]:
    st.info(f"Public holiday: {holiday_data['Holiday_Name']}")
else:
    st.caption("Today is not a public holiday.")

st.caption(f"Entry date: {entry_date.strftime('%d %B %Y')}")
st.divider()

# Products and forecasts
try:
    products = get_products()
    forecast_data = get_forecast_data(entry_date)

    if not products:
        st.warning("No bakery products were found.")
        st.stop()

    forecast_lookup = dict(
        zip(
            forecast_data["Product"],
            forecast_data["Predicted_Demand"],
        )
    )

    existing_data = load_bakery_data()
    existing_data["Date"] = pd.to_datetime(
        existing_data["Date"],
        errors="coerce",
    ).dt.date

    existing_today = existing_data[
        existing_data["Date"] == entry_date
    ]

except Exception as error:
    st.error(f"Unable to load daily entry data: {error}")
    st.stop()

existing_products = set(existing_today["Product"].astype(str))

if existing_products:
    st.info(
        "Products already recorded today are excluded to prevent "
        "duplicate entries."
    )

available_products = [
    product for product in products
    if product not in existing_products
]

if not available_products:
    st.success("All products already have entries for today.")
    st.stop()

st.markdown("### Enter Production and Sales")
st.write(
    "Enter whole-number quantities. Units sold cannot exceed "
    "units produced."
)

entry_rows = [
    {
        "Product": product,
        "Predicted Units": forecast_lookup.get(product, "-"),
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
        "Product": st.column_config.TextColumn("Product"),
        "Predicted Units": st.column_config.TextColumn(
            "Predicted Units",
            help="Saved forecast for today, if available.",
        ),
        "Units Produced": st.column_config.NumberColumn(
            "Units Produced",
            min_value=0,
            step=1,
            format="%d",
        ),
        "Units Sold": st.column_config.NumberColumn(
            "Units Sold",
            min_value=0,
            step=1,
            format="%d",
        ),
    },
    key="daily_entry_editor",
)

st.divider()

if st.button("Save Daily Entries", type="primary"):
    errors = []

    for _, item in edited_data.iterrows():
        product = item["Product"]
        produced = item["Units Produced"]
        sold = item["Units Sold"]

        if pd.isna(produced) or pd.isna(sold):
            errors.append(f"{product}: enter both quantities.")
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
            validate_daily_entry(product, int(produced), int(sold))
        except (ValueError, TypeError) as error:
            errors.append(f"{product}: {error}")

    if errors:
        for error in errors:
            st.error(error)
    else:
        latest_data = load_bakery_data()
        latest_data["Date"] = pd.to_datetime(
            latest_data["Date"],
            errors="coerce",
        ).dt.date

        latest_today = latest_data[
            latest_data["Date"] == entry_date
        ]

        latest_products = set(latest_today["Product"].astype(str))

        duplicates = [
            product for product in edited_data["Product"]
            if product in latest_products
        ]

        if duplicates:
            st.error(
                "Entries already exist for: "
                + ", ".join(duplicates)
                + ". Refresh the page before trying again."
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
                        "Leftover": calculate_leftover(produced, sold),
                    })

                st.success("Daily entries saved successfully!")
                st.markdown("### Saved Entry Summary")

                st.dataframe(
                    pd.DataFrame(saved_rows),
                    hide_index=True,
                    use_container_width=True,
                )

            except Exception as error:
                st.error(
                    "An error occurred while saving entries. "
                    "Some rows may already have been saved. Check your "
                    "CSV data before retrying. "
                    f"Details: {error}"
                )