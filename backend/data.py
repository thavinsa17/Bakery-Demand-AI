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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE_DATA_PATH = os.path.join(PROJECT_ROOT,"data","bakery_data.csv")
FORECAST_DATA_PATH = os.path.join(PROJECT_ROOT,"data","forecast_history.csv")
PRICE_HISTORY_PATH = os.path.join(PROJECT_ROOT, "data", "price_history.csv")

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
# INITIALIZE PRICE HISTORY
# ============================================================

def initialize_price_history():
    """
    Create price_history.csv if it does not already exist.

    The initial price for each product is taken from its latest
    recorded entry in bakery_data.csv.

    An existing price history file is never overwritten.
    The original bakery sales dataset is never modified.
    """

    # If the price history already exists, preserve it.
    if os.path.exists(PRICE_HISTORY_PATH):
        return

    # Load the existing live bakery dataset.
    data = load_bakery_data()

    # Do not create an empty price history from an empty dataset.
    if data.empty:
        raise ValueError(
            "Cannot initialize price history from empty bakery data."
        )

    # Ignore rows that do not contain a product or a valid price.
    data = data.dropna(
        subset=["Product", "Base_Price_LKR"]
    ).copy()

    # Ensure dates are in a consistent datetime format.
    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="raise"
    )

    # Sort by date so the latest record for each product is last.
    data = data.sort_values("Date")

    # Keep the latest recorded price for each individual product.
    latest_prices = data.drop_duplicates(
        subset=["Product"],
        keep="last"
    )

    # Keep only the fields needed for price history.
    price_history = latest_prices[
        ["Date", "Product", "Base_Price_LKR"]
    ].copy()

    # Rename Date to Effective_Date to show when the price applies.
    price_history = price_history.rename(
        columns={"Date": "Effective_Date"}
    )

    # Ensure the destination folder exists before writing the file.
    os.makedirs(
        os.path.dirname(PRICE_HISTORY_PATH),
        exist_ok=True
    )

    # Create the initial price history CSV.
    price_history.to_csv(
        PRICE_HISTORY_PATH,
        index=False
    )


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
    Return the latest known price for every bakery product.

    Initializes price_history.csv from bakery_data.csv if
    the price history file does not exist yet.

    Returns
    -------
    dict
        A dictionary mapping each product to its latest price.
    """

    # Create the price history file if it has not been initialized.
    initialize_price_history()

    # Load the separate price history CSV.
    data = pd.read_csv(PRICE_HISTORY_PATH)

    # Return an empty dictionary if there are no price records.
    if data.empty:
        return {}

    # Convert effective dates to datetime values.
    data["Effective_Date"] = pd.to_datetime(
        data["Effective_Date"],
        errors="raise"
    )

    # Sort by date so the most recent price for each product
    # appears last.
    data = data.sort_values("Effective_Date")

    # Keep the latest price record for each product.
    latest_prices = data.drop_duplicates(
        subset=["Product"],
        keep="last"
    )

    # Convert product names and prices into a dictionary.
    return (
        latest_prices
        .set_index("Product")["Base_Price_LKR"]
        .to_dict()
    )



# ============================================================
# GET PRODUCT PRICE
# ============================================================


# ============================================================
# GET PRODUCT PRICE
# ============================================================

def get_product_price(product, target_date=None):
    """
    Get a product's price for a particular date.

    If target_date is provided, return the latest price whose
    Effective_Date is on or before that date.

    If target_date is omitted, return the latest known price.
    """

    # Ensure that price history exists before reading it.
    initialize_price_history()

    # Load the separate price history file.
    data = pd.read_csv(PRICE_HISTORY_PATH)

    # Keep only records belonging to the requested product.
    product_data = data[
        data["Product"] == product
    ].copy()

    # Reject products that have no recorded price history.
    if product_data.empty:
        raise ValueError(
            f"No price history found for product: {product}"
        )

    # Convert effective dates into datetime values.
    product_data["Effective_Date"] = pd.to_datetime(
        product_data["Effective_Date"],
        errors="raise"
    )

    # If a date was provided, exclude prices that start later.
    if target_date is not None:
        target_date = pd.to_datetime(
            target_date,
            errors="raise"
        ).normalize()

        product_data = product_data[
            product_data["Effective_Date"] <= target_date
        ]

        # Reject dates earlier than the first known price.
        if product_data.empty:
            raise ValueError(
                f"No price information found for {product} "
                f"on or before {target_date.date()}."
            )

    # Sort chronologically and select the latest applicable price.
    product_data = product_data.sort_values("Effective_Date")

    return product_data.iloc[-1]["Base_Price_LKR"]



# ============================================================
# UPDATE PRODUCT PRICE
# ============================================================

def update_product_price(product, new_price, effective_date=None):
    """
    Record a new price for a product without overwriting
    previous price history or modifying sales records.

    The new price applies from effective_date onward.
    If effective_date is omitted, today's date is used.

    Returns
    -------
    bool
        True if a new price record was added.
        False if the price is already the same on that date.
    """

    from datetime import date

    # Ensure the initial price history exists.
    initialize_price_history()

    # Confirm that the requested product is in the catalogue.
    if product not in get_products():
        raise ValueError(f"Unknown bakery product: {product}")

    # Convert the new price to a number.
    try:
        new_price = float(new_price)
    except (TypeError, ValueError):
        raise ValueError("Price must be a valid number.")

    # Reject zero, negative, NaN, or infinite prices.
    import math

    if not math.isfinite(new_price) or new_price <= 0:
        raise ValueError("Price must be a positive finite number.")

    # Use today's date if no effective date was supplied.
    if effective_date is None:
        effective_date = date.today()

    # Normalize the date to remove any time component.
    effective_date = pd.to_datetime(
        effective_date,
        errors="raise"
    ).normalize()

    # Load existing price history.
    data = pd.read_csv(PRICE_HISTORY_PATH)

    # Convert stored dates for reliable comparisons.
    data["Effective_Date"] = pd.to_datetime(
        data["Effective_Date"],
        errors="raise"
    ).dt.normalize()

    # Find the latest price that applies on the change date.
    applicable_prices = data[
        (data["Product"] == product)
        & (data["Effective_Date"] <= effective_date)
    ]

    # A price cannot be changed before the product's first
    # recorded price without a known starting price.
    if applicable_prices.empty:
        raise ValueError(
            f"No existing price history for {product} "
            f"on or before {effective_date.date()}."
        )

    current_price = applicable_prices.sort_values(
        "Effective_Date"
    ).iloc[-1]["Base_Price_LKR"]

    # Avoid recording a duplicate price change when the price
    # is already the same on the effective date.
    if float(current_price) == new_price:
        return False

    # Reject conflicting price records for the same product/date.
    same_date = data[
        (data["Product"] == product)
        & (data["Effective_Date"] == effective_date)
    ]

    if not same_date.empty:
        # Replace only the record for this product and date.
        # Other dates and products remain unchanged.
        data = data[
            ~(
                (data["Product"] == product)
                & (data["Effective_Date"] == effective_date)
            )
        ]

    # Build a new price-history record.
    new_record = pd.DataFrame([{
        "Effective_Date": effective_date,
        "Product": product,
        "Base_Price_LKR": new_price,
    }])

    # Add the new record while preserving earlier history.
    data = pd.concat(
        [data, new_record],
        ignore_index=True
    )

    # Sort records for readability and reliable future lookups.
    data = data.sort_values(
        ["Effective_Date", "Product"]
    ).reset_index(drop=True)

    # Save only the price history file.
    data.to_csv(PRICE_HISTORY_PATH, index=False)

    return True


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


# ============================================================
# SAVE FORECASTS
# ============================================================

def save_forecasts(forecasts):
    """
    Save forecasts to forecast_history.csv.

    Creates the CSV if it does not exist and replaces
    existing records with matching Date + Product keys.
    """

    columns = ["Date", "Product", "Predicted_Demand"]

    if not forecasts:
        raise ValueError("Cannot save an empty forecast batch.")

    forecast_data = pd.DataFrame(forecasts)

    missing_columns = [
        column for column in columns
        if column not in forecast_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Forecasts are missing columns: {missing_columns}"
        )

    forecast_data = forecast_data[columns].copy()
    forecast_data["Date"] = pd.to_datetime(
        forecast_data["Date"], errors="raise"
    ).dt.normalize()

    if forecast_data["Product"].isna().any():
        raise ValueError("Forecast product names cannot be empty.")

    if forecast_data["Date"].isna().any():
        raise ValueError("Forecast dates cannot be empty.")

    if forecast_data["Predicted_Demand"].isna().any():
        raise ValueError("Predicted demand cannot be empty.")

    if (forecast_data["Predicted_Demand"] < 0).any():
        raise ValueError("Predicted demand cannot be negative.")

    forecast_data["Product"] = forecast_data["Product"].astype(str)

    if forecast_data["Product"].str.strip().eq("").any():
        raise ValueError("Forecast product names cannot be empty.")

    if forecast_data.duplicated(["Date", "Product"]).any():
        raise ValueError(
            "A forecast batch contains duplicate Date + Product records."
        )

    valid_products = get_products()

    if not forecast_data["Product"].isin(valid_products).all():
        raise ValueError("Forecast batch contains an unknown product.")

    if not os.path.exists(FORECAST_DATA_PATH):
        os.makedirs(os.path.dirname(FORECAST_DATA_PATH), exist_ok=True)
        forecast_data.to_csv(FORECAST_DATA_PATH, index=False)
        return

    existing_data = pd.read_csv(FORECAST_DATA_PATH)

    if existing_data.empty:
        existing_data = pd.DataFrame(columns=columns)
    elif not set(columns).issubset(existing_data.columns):
        raise ValueError("Forecast history CSV has an invalid structure.")

    if not existing_data.empty:
        existing_data["Date"] = pd.to_datetime(
            existing_data["Date"], errors="raise"
        ).dt.normalize()

    forecast_keys = pd.MultiIndex.from_frame(
        forecast_data[["Date", "Product"]]
    )

    if not existing_data.empty:
        existing_keys = pd.MultiIndex.from_frame(
            existing_data[["Date", "Product"]]
        )

        existing_data = existing_data[
            ~existing_keys.isin(forecast_keys)
        ]

    updated_data = pd.concat(
        [existing_data[columns], forecast_data],
        ignore_index=True
    )

    updated_data = updated_data.sort_values(
        ["Date", "Product"]
    ).reset_index(drop=True)

    updated_data.to_csv(FORECAST_DATA_PATH, index=False)



# ============================================================
# GET FORECASTS FOR A DATE
# ============================================================

def get_forecast_data(target_date):
    """
    Return a prediction for every product on the requested date.

    Products without saved predictions receive "-" for display.
    """

    products = get_products()

    result = pd.DataFrame({
        "Product": products,
        "Predicted_Demand": ["-"] * len(products)
    })

    if not os.path.exists(FORECAST_DATA_PATH):
        return result

    target_date = pd.to_datetime(target_date, errors="raise").normalize()

    data = pd.read_csv(FORECAST_DATA_PATH)

    if data.empty:
        return result

    required_columns = [
        "Date",
        "Product",
        "Predicted_Demand"
    ]

    if not set(required_columns).issubset(data.columns):
        raise ValueError("Forecast history CSV has an invalid structure.")

    data["Date"] = pd.to_datetime(
        data["Date"], errors="raise"
    ).dt.normalize()

    saved_forecasts = data[data["Date"] == target_date]

    if saved_forecasts["Product"].duplicated().any():
        raise ValueError(
            "Forecast history contains duplicate products for this date."
        )

    saved_forecasts = saved_forecasts.set_index("Product")[
        "Predicted_Demand"
    ]

    result["Predicted_Demand"] = result["Product"].map(
        saved_forecasts
    ).fillna("-")

    return result
