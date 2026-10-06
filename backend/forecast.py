"""
backend/forecast.py

Handles tomorrow's bakery demand forecasting.

This module combines:
    1. Tomorrow's date and calendar information.
    2. Tomorrow's holiday information.
    3. Tomorrow's weather forecast.
    4. Product information and prices.
    5. The trained demand prediction model.

The final result is a demand prediction for every bakery product.
"""

# ============================================================
# IMPORTS
# ============================================================

from datetime import date, timedelta

from backend.data import get_products, get_product_price
from backend.holidays import get_holiday_info
from backend.weather import get_tomorrow_weather
from ml.predict import predict_product_demand


# ============================================================
# SEASON HELPER
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
# CREATE TOMORROW'S FEATURES
# ============================================================

def create_tomorrow_features(product, target_date, weather_data, holiday_data):
    """
    Create the model input for one product for a target date.
    """

    month = target_date.month

    product_data = {
        "Product": product,
        "Day_of_Week": target_date.strftime("%A"),
        "Month": month,
        "Season": get_season(month),
        "Is_Weekend": target_date.weekday() >= 5,
        "Temperature_C": weather_data["Temperature_C"],
        "Rainfall_mm": weather_data["Rainfall_mm"],
        "Weather_Condition": weather_data["Weather_Condition"],
        "Is_Holiday": holiday_data["Is_Holiday"],
        "Day_Before_Holiday": holiday_data["Day_Before_Holiday"],
        "Day_After_Holiday": holiday_data["Day_After_Holiday"],
        "Base_Price_LKR": get_product_price(
            product,
            target_date
        )
    }

    return product_data


# ============================================================
# FORECAST ONE PRODUCT
# ============================================================

def forecast_product(product, target_date=None):
    """
    Forecast demand for one bakery product.

    Parameters
    ----------
    product : str
        Bakery product name.

    target_date : date, optional
        Date to forecast.
        Defaults to tomorrow.

    Returns
    -------
    dict
        Forecast information for the product.
    """

    if target_date is None:
        target_date = date.today() + timedelta(days=1)

    weather_data = get_tomorrow_weather()

    holiday_data = get_holiday_info(target_date)

    product_data = create_tomorrow_features(
        product,
        target_date,
        weather_data,
        holiday_data
    )

    prediction = predict_product_demand(product_data)

    return {
        "Date": target_date.isoformat(),
        "Product": product,
        "Predicted_Demand": prediction,
        "Base_Price_LKR": product_data["Base_Price_LKR"],
        "Temperature_C": weather_data["Temperature_C"],
        "Rainfall_mm": weather_data["Rainfall_mm"],
        "Weather_Condition": weather_data["Weather_Condition"],
        "Is_Holiday": holiday_data["Is_Holiday"],
        "Holiday_Name": holiday_data["Holiday_Name"]
    }


# ============================================================
# FORECAST ALL PRODUCTS
# ============================================================

def forecast_all_products(target_date=None):
    """
    Forecast demand for every bakery product.

    Returns
    -------
    list
        A list containing one forecast dictionary per product.
    """

    if target_date is None:
        target_date = date.today() + timedelta(days=1)

    weather_data = get_tomorrow_weather()
    holiday_data = get_holiday_info(target_date)

    forecasts = []

    for product in get_products():

        product_data = create_tomorrow_features(
            product,
            target_date,
            weather_data,
            holiday_data
        )

        prediction = predict_product_demand(product_data)

        forecasts.append({
            "Date": target_date.isoformat(),
            "Product": product,
            "Predicted_Demand": prediction,
            "Base_Price_LKR": product_data["Base_Price_LKR"],
            "Temperature_C": weather_data["Temperature_C"],
            "Rainfall_mm": weather_data["Rainfall_mm"],
            "Weather_Condition": weather_data["Weather_Condition"],
            "Is_Holiday": holiday_data["Is_Holiday"],
            "Holiday_Name": holiday_data["Holiday_Name"]
        })

    return forecasts