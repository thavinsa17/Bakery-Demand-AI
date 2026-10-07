"""
setup/initialize_data.py

Creates the initial live bakery dataset.

This script:

    1. Reads the original bakery sales CSV.
    2. Retrieves historical weather data.
    3. Retrieves historical Sri Lankan holiday information.
    4. Creates calendar features.
    5. Calculates leftover units.
    6. Combines everything into one dataset.
    7. Saves the result as data/bakery_data.csv.

IMPORTANT:
    The original CSV is NEVER modified.
"""


import os
import sys

import pandas as pd


# ---------------------------------------------------------
# Allow imports from the project root
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------
# Import our backend modules
# ---------------------------------------------------------

from backend.weather import get_historical_weather
from backend.holidays import get_historical_holidays


# ---------------------------------------------------------
# File locations
# ---------------------------------------------------------

ORIGINAL_DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "kandy_bakery_sales_2024_2025.csv"
)

LIVE_DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "bakery_data.csv"
)


# ---------------------------------------------------------
# Calendar feature helper
# ---------------------------------------------------------

def get_season(month):
    """
    Determine the Sri Lankan climatic season based on month.
    """

    if month in [12, 1, 2]:
        return "Northeast Monsoon"

    elif month in [3, 4]:
        return "First Inter-monsoon"

    elif month in [5, 6, 7, 8, 9]:
        return "Southwest Monsoon"

    else:
        return "Second Inter-monsoon"


def add_calendar_features(data):
    """
    Add calendar-related features to the sales dataset.
    """

    data["Date"] = pd.to_datetime(data["Date"])

    # Day name such as Monday, Tuesday, etc.
    data["Day_of_Week"] = data["Date"].dt.day_name()

    # Month number: January = 1, December = 12
    data["Month"] = data["Date"].dt.month

    # Sri Lankan climatic season
    data["Season"] = data["Month"].apply(get_season)

    # True for Saturday and Sunday
    data["Is_Weekend"] = data["Date"].dt.dayofweek >= 5

    return data


# ---------------------------------------------------------
# Main initialization function
# ---------------------------------------------------------

def initialize_data():
    """
    Create the initial bakery_data.csv file.
    """

    print("\n========================================")
    print(" Bakery Demand Dataset Initialization")
    print("========================================\n")


    # -----------------------------------------------------
    # Step 1: Read original CSV
    # -----------------------------------------------------

    print("Step 1: Reading original sales data...")

    if not os.path.exists(ORIGINAL_DATA_PATH):
        raise FileNotFoundError(
            f"Original CSV was not found:\n{ORIGINAL_DATA_PATH}"
        )

    data = pd.read_csv(ORIGINAL_DATA_PATH)

    print(f"Loaded {len(data):,} sales records.")


    # -----------------------------------------------------
    # Step 2: Validate required columns
    # -----------------------------------------------------

    required_columns = [
        "Date",
        "Product",
        "Base_Price_LKR",
        "Units_Produced",
        "Units_Sold"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Original CSV is missing these columns: "
            f"{missing_columns}"
        )


    # -----------------------------------------------------
    # Step 3: Convert dates
    # -----------------------------------------------------

    data["Date"] = pd.to_datetime(data["Date"])

    start_date = data["Date"].min().date()
    end_date = data["Date"].max().date()

    print(f"Historical period: {start_date} → {end_date}")


    # -----------------------------------------------------
    # Step 4: Calculate leftover
    # -----------------------------------------------------

    print("\nStep 2: Calculating leftover units...")

    data["Leftover"] = (
        data["Units_Produced"] - data["Units_Sold"]
    )


    # -----------------------------------------------------
    # Step 5: Add calendar features
    # -----------------------------------------------------

    print("Step 3: Adding calendar features...")

    data = add_calendar_features(data)


    # -----------------------------------------------------
    # Step 6: Retrieve historical weather
    # -----------------------------------------------------

    print("\nStep 4: Retrieving historical weather...")

    weather_data = get_historical_weather(
        start_date.isoformat(),
        end_date.isoformat()
    )

    print(
        f"Retrieved weather for "
        f"{len(weather_data):,} dates."
    )


    # -----------------------------------------------------
    # Step 7: Retrieve historical holidays
    # -----------------------------------------------------

    print("\nStep 5: Retrieving historical holidays...")

    holiday_data = get_historical_holidays(
        start_date.isoformat(),
        end_date.isoformat()
    )

    print(
        f"Retrieved holiday information for "
        f"{len(holiday_data):,} dates."
    )


    # -----------------------------------------------------
    # Step 8: Prepare dates for merging
    # -----------------------------------------------------

    weather_data["Date"] = pd.to_datetime(
        weather_data["Date"]
    )

    holiday_data["Date"] = pd.to_datetime(
        holiday_data["Date"]
    )


    # -----------------------------------------------------
    # Step 9: Merge weather information
    # -----------------------------------------------------

    print("\nStep 6: Combining weather information...")

    data = data.merge(
        weather_data,
        on="Date",
        how="left"
    )


    # -----------------------------------------------------
    # Step 10: Merge holiday information
    # -----------------------------------------------------

    print("Step 7: Combining holiday information...")

    data = data.merge(
        holiday_data,
        on="Date",
        how="left"
    )


    # -----------------------------------------------------
    # Step 11: Order the columns
    # -----------------------------------------------------

    final_columns = [
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

    data = data[final_columns]


    # -----------------------------------------------------
    # Step 12: Sort the dataset
    # -----------------------------------------------------

    data = data.sort_values(
        by=["Date", "Product"]
    ).reset_index(drop=True)


    # -----------------------------------------------------
    # Step 13: Basic validation
    # -----------------------------------------------------

    print("\nStep 8: Validating dataset...")

    missing_values = data.isnull().sum()

    columns_with_missing_values = (
        missing_values[missing_values > 0]
    )

    if len(columns_with_missing_values) > 0:

        print("\nWARNING: Missing values found:")

        print(columns_with_missing_values)

    else:

        print("No missing values found.")


    # -----------------------------------------------------
    # Step 14: Save live dataset
    # -----------------------------------------------------

    print("\nStep 9: Saving live dataset...")

    data.to_csv(
        LIVE_DATA_PATH,
        index=False
    )


    # -----------------------------------------------------
    # Step 15: Final summary
    # -----------------------------------------------------

    print("\n========================================")
    print(" Initialization Complete!")
    print("========================================")

    print(f"\nOutput file:")
    print(LIVE_DATA_PATH)

    print(f"\nRows: {len(data):,}")
    print(f"Columns: {len(data.columns)}")

    print("\nColumns:")
    for column in data.columns:
        print(f"  - {column}")

    print("\nFirst 5 rows:")
    print(data.head().to_string(index=False))

    print("\n")


# ---------------------------------------------------------
# Run initialization
# ---------------------------------------------------------

if __name__ == "__main__":
    initialize_data()