"""
backend/data.py

Handles all operations involving the live bakery dataset.

This module is responsible for:
    1. Loading bakery_data.csv.
    2. Reading available products and prices.
    3. Validating daily sales entries.
    4. Calculating leftover units.
    5. Adding new daily records.
    6. Saving the updated live dataset.

The original historical CSV is never modified.
"""

# ============================================================
# IMPORTS
# ============================================================

import os
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LIVE_DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "bakery_data.csv"
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "Date",
    "Product",
    "Base_Price_LKR",
    "Units_Produced",
    "Units_Sold",
    "Leftover",
    "Day_of_Week",
    "Month",
    "Season",
    "Is_Weekend",
    "Temperature_C",
    "Rainfall_mm",
    "Weather_Code",
    "Weather_Condition",
    "Is_Holiday",
    "Holiday_Name",
    "Day_Before_Holiday",
    "Day_After_Holiday"
]


# ============================================================
# LOAD LIVE DATA
# ============================================================

def load_bakery_data():
    """
    Load the live bakery dataset.

    Returns
    -------
    pandas.DataFrame
        The current bakery dataset.
    """

    if not os.path.exists(LIVE_DATA_PATH):
        raise FileNotFoundError(
            f"Live bakery dataset was not found:\n{LIVE_DATA_PATH}"
        )

    data = pd.read_csv(LIVE_DATA_PATH)

    data["Date"] = pd.to_datetime(data["Date"])

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Live dataset is missing columns: {missing_columns}"
        )

    return data


# ============================================================
# SAVE LIVE DATA
# ============================================================

def save_bakery_data(data):
    """
    Save the updated live bakery dataset.

    The original historical CSV is never modified.
    """

    data = data.copy()

    data["Date"] = pd.to_datetime(data["Date"])

    data = data.sort_values(
        by=["Date", "Product"]
    ).reset_index(drop=True)

    data.to_csv(
        LIVE_DATA_PATH,
        index=False
    )


# ============================================================
# GET PRODUCTS
# ============================================================

def get_products():
    """
    Return the fixed bakery product catalogue.

    Returns
    -------
    list
        Product names available in the dataset.
    """

    data = load_bakery_data()

    products = (
        data["Product"]
        .dropna()
        .unique()
        .tolist()
    )

    return sorted(products)


# ============================================================
# GET PRODUCT PRICES
# ============================================================

def get_product_prices():
    """
    Return the current base price for each product.

    Returns
    -------
    dict
        Dictionary in the form:
        {
            "Chicken Bun": 100,
            "Fish Bun": 120
        }
    """

    data = load_bakery_data()

    prices = (
        data[["Product", "Base_Price_LKR"]]
        .drop_duplicates("Product")
        .set_index("Product")["Base_Price_LKR"]
        .to_dict()
    )

    return prices


# ============================================================
# GET PRODUCT PRICE
# ============================================================

def get_product_price(product, target_date=None):
    """
    Get the base price of one product.

    If target_date is supplied, the price from the latest
    record on or before that date is returned.

    This allows future price changes to preserve historical
    prices.
    """

    data = load_bakery_data()

    product_data = data[
        data["Product"] == product
    ].copy()

    if product_data.empty:
        raise ValueError(
            f"Unknown bakery product: {product}"
        )

    if target_date is not None:
        target_date = pd.to_datetime(target_date)

        product_data = product_data[
            product_data["Date"] <= target_date
        ]

        if product_data.empty:
            raise ValueError(
                f"No price information found for {product} "
                f"on or before {target_date.date()}."
            )

    product_data = product_data.sort_values("Date")

    return product_data.iloc[-1]["Base_Price_LKR"]


# ============================================================
# GET LATEST DATE
# ============================================================

def get_latest_date():
    """
    Return the latest date currently stored in the live dataset.
    """

    data = load_bakery_data()

    return data["Date"].max().date()


# ============================================================
# CHECK DAILY ENTRY
# ============================================================

def daily_entry_exists(target_date):
    """
    Check whether sales records already exist for a date.
    """

    data = load_bakery_data()

    target_date = pd.to_datetime(target_date).date()

    return (
        data["Date"].dt.date == target_date
    ).any()


# ============================================================
# VALIDATE DAILY ENTRY
# ============================================================

def validate_daily_entry(product, units_produced, units_sold):
    """
    Validate the production and sales values for one product.
    """

    if product not in get_products():
        raise ValueError(
            f"Unknown bakery product: {product}"
        )

    if pd.isna(units_produced) or pd.isna(units_sold):
        raise ValueError(
            "Units produced and units sold are required."
        )

    if units_produced < 0:
        raise ValueError(
            "Units produced cannot be negative."
        )

    if units_sold < 0:
        raise ValueError(
            "Units sold cannot be negative."
        )

    if units_sold > units_produced:
        raise ValueError(
            "Units sold cannot be greater than units produced."
        )


# ============================================================
# CALCULATE LEFTOVER
# ============================================================

def calculate_leftover(units_produced, units_sold):
    """
    Calculate leftover units.
    """

    validate_units(
        units_produced,
        units_sold
    )

    return units_produced - units_sold


# ============================================================
# VALIDATE UNITS
# ============================================================

def validate_units(units_produced, units_sold):
    """
    Validate production and sales quantities.
    """

    if pd.isna(units_produced) or pd.isna(units_sold):
        raise ValueError(
            "Units produced and units sold are required."
        )

    if units_produced < 0:
        raise ValueError(
            "Units produced cannot be negative."
        )

    if units_sold < 0:
        raise ValueError(
            "Units sold cannot be negative."
        )

    if units_sold > units_produced:
        raise ValueError(
            "Units sold cannot be greater than units produced."
        )


# ============================================================
# ADD DAILY ENTRY
# ============================================================

def add_daily_entry(
    target_date,
    product,
    units_produced,
    units_sold,
    weather_data,
    holiday_data
):
    """
    Add one completed daily sales record to the live dataset.

    Parameters
    ----------
    target_date : date or str
        Date of the sales record.

    product : str
        Bakery product.

    units_produced : int
        Number of units produced.

    units_sold : int
        Number of units sold.

    weather_data : dict
        Weather information for the date.

    holiday_data : dict
        Holiday information for the date.

    Returns
    -------
    pandas.DataFrame
        Updated bakery dataset.
    """

    target_date = pd.to_datetime(target_date)

    validate_daily_entry(
        product,
        units_produced,
        units_sold
    )

    data = load_bakery_data()

    # Prevent duplicate product records for the same date.
    duplicate = (
        (data["Date"] == target_date) &
        (data["Product"] == product)
    )

    if duplicate.any():
        raise ValueError(
            f"A record already exists for {product} "
            f"on {target_date.date()}."
        )

    # Get the applicable product price.
    base_price = get_product_price(
        product,
        target_date
    )

    # Calendar information.
    day_of_week = target_date.day_name()
    month = target_date.month
    season = get_season(month)
    is_weekend = target_date.dayofweek >= 5

    # Calculate leftover.
    leftover = calculate_leftover(
        units_produced,
        units_sold
    )

    # Create the new record.
    new_record = {
        "Date": target_date,
        "Product": product,
        "Base_Price_LKR": base_price,
        "Units_Produced": units_produced,
        "Units_Sold": units_sold,
        "Leftover": leftover,
        "Day_of_Week": day_of_week,
        "Month": month,
        "Season": season,
        "Is_Weekend": is_weekend,
        "Temperature_C": weather_data["Temperature_C"],
        "Rainfall_mm": weather_data["Rainfall_mm"],
        "Weather_Code": weather_data["Weather_Code"],
        "Weather_Condition": weather_data["Weather_Condition"],
        "Is_Holiday": holiday_data["Is_Holiday"],
        "Holiday_Name": holiday_data["Holiday_Name"],
        "Day_Before_Holiday": holiday_data["Day_Before_Holiday"],
        "Day_After_Holiday": holiday_data["Day_After_Holiday"]
    }

    new_record_df = pd.DataFrame([new_record])

    data = pd.concat(
        [data, new_record_df],
        ignore_index=True
    )

    save_bakery_data(data)

    return data


# ============================================================
# CALENDAR SEASON
# ============================================================

def get_season(month):
    """
    Determine the Sri Lankan climatic season from the month.
    """

    if month in [12, 1, 2]:
        return "Northeast Monsoon"

    if month in [3, 4]:
        return "First Inter-monsoon"

    if month in [5, 6, 7, 8, 9]:
        return "Southwest Monsoon"

    return "Second Inter-monsoon"