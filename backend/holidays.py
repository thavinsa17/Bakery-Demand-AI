"""
backend/holidays.py

Handles all holiday-related operations for the bakery demand
forecasting application.

This module uses the Python 'holidays' library to determine
Sri Lankan government holidays.
"""

import holidays as holidays_lib
import pandas as pd
from datetime import timedelta


# ---------------------------------------------------------
# Sri Lankan holiday calendar
# ---------------------------------------------------------

SRI_LANKA_HOLIDAYS = holidays_lib.country_holidays("LK")


# ---------------------------------------------------------
# Get holiday information for one date
# ---------------------------------------------------------

def get_holiday_info(target_date):
    """
    Get holiday information for a single date.

    Returns:
        A dictionary containing:
            Date
            Is_Holiday
            Holiday_Name
            Day_Before_Holiday
            Day_After_Holiday
    """

    # Convert the input into a Python date object.
    target_date = pd.to_datetime(target_date).date()

    # Is the date itself a holiday?
    is_holiday = target_date in SRI_LANKA_HOLIDAYS

    # Get the holiday name.
    holiday_name = SRI_LANKA_HOLIDAYS.get(target_date, "")

    # Dates immediately before and after.
    previous_date = target_date - timedelta(days=1)
    next_date = target_date + timedelta(days=1)

    # Check whether the surrounding dates are holidays.
    day_before_holiday = next_date in SRI_LANKA_HOLIDAYS
    day_after_holiday = previous_date in SRI_LANKA_HOLIDAYS

    return {
        "Date": target_date.isoformat(),
        "Is_Holiday": is_holiday,
        "Holiday_Name": holiday_name,
        "Day_Before_Holiday": day_before_holiday,
        "Day_After_Holiday": day_after_holiday
    }


# ---------------------------------------------------------
# Get historical holiday information
# ---------------------------------------------------------

def get_historical_holidays(start_date, end_date):
    """
    Get holiday information for every date between
    start_date and end_date.
    """

    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D"
    )

    holiday_data = []

    for current_date in dates:
        holiday_info = get_holiday_info(current_date)
        holiday_data.append(holiday_info)

    return pd.DataFrame(holiday_data)