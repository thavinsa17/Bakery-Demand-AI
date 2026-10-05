import streamlit as st

from utils.ui import page_header, require_login


require_login()

page_header(
    "Bakery Profile",
    "View and manage your bakery information and product prices."
)


# -----------------------------
# Bakery Information
# -----------------------------

st.subheader("Bakery Information")

bakery_name = st.text_input(
    "Bakery Name",
    value="My Bakery"
)

address = st.text_area(
    "Bakery Address",
    value="Colombo, Sri Lanka"
)

col1, col2 = st.columns(2)

with col1:
    latitude = st.number_input(
        "Latitude",
        value=6.927100,
        format="%.6f"
    )

with col2:
    longitude = st.number_input(
        "Longitude",
        value=79.861200,
        format="%.6f"
    )

contact_number = st.text_input(
    "Contact Number"
)


# -----------------------------
# Products & Base Prices
# -----------------------------

st.subheader("Products & Base Prices")

st.write(
    "Product names are fixed. "
    "Edit the base prices directly in the table."
)


# Temporary product catalogue.
# This will later come from the backend/database.

products = [
    {
        "Product": "Croissant",
        "Base Price (Rs.)": 150.00
    },
    {
        "Product": "Chocolate Cake",
        "Base Price (Rs.)": 850.00
    },
    {
        "Product": "Chicken Puff",
        "Base Price (Rs.)": 180.00
    },
    {
        "Product": "Fish Bun",
        "Base Price (Rs.)": 120.00
    },
]


edited_products = st.data_editor(
    products,
    column_config={
        "Product": st.column_config.TextColumn(
            "Product",
            disabled=True
        ),
        "Base Price (Rs.)": st.column_config.NumberColumn(
            "Base Price (Rs.)",
            min_value=0,
            step=10,
            format="%.2f"
        )
    },
    hide_index=True,
    use_container_width=True,
    num_rows="fixed"
)


# -----------------------------
# Save Profile
# -----------------------------

if st.button("Save Profile", type="primary"):

    if not bakery_name:
        st.error("Please enter the bakery name.")

    elif not address:
        st.error("Please enter the bakery address.")

    elif not contact_number:
        st.error("Please enter the bakery contact number.")

    else:
        st.success("Bakery profile updated successfully!")