import streamlit as st
import pandas as pd
from datetime import date

from utils.ui import page_header, require_login
from backend.data import (
    get_products,
    get_product_prices,
    get_product_price,
    update_product_price,
)

st.set_page_config(
    page_title="Bakery Profile",
    page_icon="🥐",
    layout="wide",
)

require_login()

page_header(
    "Bakery Profile",
    "View your bakery information and manage product prices.",
)


# ------------------------------------------------------------
# BAKERY INFORMATION
# ------------------------------------------------------------

st.subheader("Bakery Information")

st.info(
    "Bakery details displayed here are currently for the interface only. "
    "They are not saved persistently by the backend yet."
)

bakery_name = st.text_input(
    "Bakery Name",
    value="Kandy Bakery",
)

address = st.text_area(
    "Bakery Address",
    value="Kandy, Sri Lanka",
)

col1, col2 = st.columns(2)

with col1:
    latitude = st.number_input(
        "Latitude",
        value=7.2906,
        format="%.6f",
    )

with col2:
    longitude = st.number_input(
        "Longitude",
        value=80.6337,
        format="%.6f",
    )

contact_number = st.text_input(
    "Contact Number",
)

st.divider()


# ------------------------------------------------------------
# CURRENT PRODUCT PRICES
# ------------------------------------------------------------

st.subheader("Products & Prices")

st.write(
    "These prices are loaded from the backend price history. "
    "Changing a price creates a new price record rather than "
    "overwriting the previous price."
)

try:
    products = get_products()
    prices = get_product_prices()

    if not products:
        st.warning("No products were found in the bakery data.")
        st.stop()

    price_rows = [
        {
            "Product": product,
            "Current Price (LKR)": prices.get(product),
        }
        for product in products
    ]

    st.dataframe(
        pd.DataFrame(price_rows),
        hide_index=True,
        use_container_width=True,
    )

except Exception as error:
    st.error(f"Could not load product prices: {error}")
    st.stop()


# ------------------------------------------------------------
# UPDATE A PRODUCT PRICE
# ------------------------------------------------------------

st.subheader("Update Product Price")

selected_product = st.selectbox(
    "Select Product",
    options=products,
)

try:
    current_price = float(get_product_price(selected_product))
except Exception as error:
    st.error(f"Could not load the selected product's price: {error}")
    st.stop()

st.metric(
    "Current Price",
    f"LKR {current_price:,.2f}",
)

with st.form("update_price_form"):
    new_price = st.number_input(
        "New Price (LKR)",
        min_value=0.01,
        value=max(0.01, current_price),
        step=10.0,
        format="%.2f",
    )

    effective_date = st.date_input(
        "Price Effective From",
        value=date.today(),
        min_value=date.today(),
        help="The new price will apply from this date onward.",
    )

    submitted = st.form_submit_button(
        "Save New Price",
        type="primary",
    )

if submitted:
    try:
        changed = update_product_price(
            product=selected_product,
            new_price=new_price,
            effective_date=effective_date,
        )

        if changed:
            st.success(
                f"Price for {selected_product} updated to "
                f"LKR {new_price:,.2f}, effective "
                f"{effective_date.strftime('%d %b %Y')}."
            )
            st.rerun()
        else:
            st.info(
                "This product already has that price effective "
                "on the selected date. No change was needed."
            )

    except Exception as error:
        st.error(f"Could not update the product price: {error}")