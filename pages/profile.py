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

st.set_page_config(page_title="Bakery Profile", layout="wide")

require_login()

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .profile-card {
        background-color: #FFFFFF;
        border: 1px solid #E5D7C7;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
    }

    .profile-label {
        color: #806B5B;
        font-size: 0.85rem;
        margin-bottom: 5px;
    }

    .profile-value {
        color: #49352B;
        font-size: 1.15rem;
        font-weight: 600;
    }

    div.stButton > button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

page_header(
    "Bakery Profile",
    "Manage your bakery information and keep product prices up to date.",
)

st.divider()

# Bakery information
st.subheader("Bakery Information")
st.caption("Review your bakery's basic details.")

col1, col2 = st.columns(2)

with col1:
    bakery_name = st.text_input("Bakery Name", value="Kandy Bakery")
    location = st.text_input("Location", value="Kandy, Sri Lanka")
    contact_number = st.text_input("Contact Number", placeholder="Enter contact number")

with col2:
    latitude = st.number_input(
        "Latitude",
        value=7.2906,
        format="%.4f",
        help="The bakery's geographical latitude.",
    )
    longitude = st.number_input(
        "Longitude",
        value=80.6337,
        format="%.4f",
        help="The bakery's geographical longitude.",
    )

st.info(
    "These bakery details are currently displayed in the interface only. "
    "They are not saved when you leave this page."
)

st.divider()

# Current product prices
st.subheader("Product Price List")
st.caption("View the latest recorded price for each bakery product.")

prices = get_product_prices()

if prices:
    price_df = pd.DataFrame(
        [
            {"Product": product, "Current Price (LKR)": price}
            for product, price in sorted(prices.items())
        ]
    )

    st.dataframe(
        price_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product": st.column_config.TextColumn("Product"),
            "Current Price (LKR)": st.column_config.NumberColumn(
                "Current Price (LKR)",
                format="Rs. %.2f",
            ),
        },
    )
else:
    st.warning("No product prices are available yet.")

st.divider()

# Update a product price
st.subheader("Update Product Price")
st.caption(
    "Record a new price for a product. The new price applies from the selected date."
)

products = get_products()

if products:
    with st.form("update_product_price_form"):
        selected_product = st.selectbox("Select Product", products)

        current_price = get_product_price(selected_product)

        if current_price is not None:
            st.write(f"Current price: **LKR {current_price:,.2f}**")

        new_price = st.number_input(
            "New Price (LKR)",
            min_value=0.01,
            value=(
                float(current_price)
                if current_price is not None and float(current_price) > 0
                else 100.0
            ),
            step=5.0,
            format="%.2f",
        )

        effective_date = st.date_input(
            "Effective From",
            value=date.today(),
            min_value=date.today(),
        )

        submitted = st.form_submit_button(
            "Save New Price",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                updated = update_product_price(
                    selected_product,
                    new_price,
                    effective_date,
                )

                if updated:
                    st.success(
                        f"{selected_product}'s price has been updated to "
                        f"LKR {new_price:,.2f}, effective {effective_date:%d %b %Y}."
                    )
                    st.rerun()
                else:
                    st.warning(
                        "This price is already recorded for that effective date. "
                        "Choose a different price or date."
                    )

            except Exception as error:
                st.error("Unable to update the product price.")
                st.exception(error)
else:
    st.warning("No products were found. Add product data before updating prices.")