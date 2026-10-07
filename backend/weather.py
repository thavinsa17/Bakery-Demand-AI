"""
backend/weather.py

Handles all weather-related operations for the bakery demand
forecasting application.

This module communicates with the Open-Meteo API and provides
weather information to the rest of the application.

The rest of the project does NOT need to know how Open-Meteo
works. It can simply call the functions in this file.

Main responsibilities:
    1. Retrieve historical weather for data initialization.
    2. Retrieve today's observed/recent weather.
    3. Retrieve tomorrow's weather forecast.
    4. Convert Open-Meteo WMO weather codes into readable
       weather conditions.
"""

# ============================================================
# IMPORTS
# ============================================================

import requests
import pandas as pd
from datetime import date, timedelta

from config import BAKERY


# ============================================================
# API CONFIGURATION
# ============================================================

# Open-Meteo historical weather API.
HISTORICAL_API_URL = "https://archive-api.open-meteo.com/v1/archive"

# Open-Meteo forecast API.
FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"


# ============================================================
# WEATHER CODE CONVERSION
# ============================================================

def weather_code_to_condition(weather_code):
    """
    Convert an Open-Meteo WMO weather code into a readable
    weather condition.

    Open-Meteo uses WMO weather interpretation codes.

    Parameters
    ----------
    weather_code : int
        WMO weather code returned by Open-Meteo.

    Returns
    -------
    str
        Human-readable weather condition.
    """

    # Clear sky
    if weather_code == 0:
        return "Clear"

    # Mainly clear, partly cloudy, overcast
    elif weather_code in [1, 2, 3]:
        return "Cloudy"

    # Fog
    elif weather_code in [45, 48]:
        return "Fog"

    # Drizzle
    elif weather_code in [51, 53, 55, 56, 57]:
        return "Drizzle"

    # Rain
    elif weather_code in [61, 63, 65, 66, 67]:
        return "Rain"

    # Snow
    elif weather_code in [71, 73, 75, 77]:
        return "Snow"

    # Rain showers
    elif weather_code in [80, 81, 82]:
        return "Rain Showers"

    # Snow showers
    elif weather_code in [85, 86]:
        return "Snow Showers"

    # Thunderstorms
    elif weather_code in [95, 96, 99]:
        return "Thunderstorm"

    # Unknown/unmapped code
    else:
        return "Unknown"


# ============================================================
# HISTORICAL WEATHER
# ============================================================

def get_historical_weather(start_date, end_date):
    """
    Retrieve historical daily weather for the bakery location.

    This function is primarily used by setup/initialize_data.py
    when creating bakery_data.csv from the original historical
    sales dataset.

    Parameters
    ----------
    start_date : str
        Starting date in YYYY-MM-DD format.

    end_date : str
        Ending date in YYYY-MM-DD format.

    Returns
    -------
    pandas.DataFrame
        One row per date containing:
            Date
            Temperature_C
            Rainfall_mm
            Weather_Code
            Weather_Condition
    """

    # Get the bakery coordinates from config.py.
    latitude = BAKERY["latitude"]
    longitude = BAKERY["longitude"]

    # Parameters requested from Open-Meteo.
    #
    # temperature_2m_mean: Mean daily temperature at 2 metres above ground.
    # rain_sum: Total rain during the day in millimetres.
    # weather_code: Most severe weather condition for the day.
    #
    # We also specify the timezone because Open-Meteo requires
    # a timezone when requesting daily variables.
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_mean",
            "rain_sum",
            "weather_code"
        ],
        "timezone": "auto",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm"
    }

    try:
        # Send the request to Open-Meteo.
        response = requests.get(
            HISTORICAL_API_URL,
            params=params,
            timeout=30
        )

        # Raise an error if Open-Meteo returns an HTTP error.
        response.raise_for_status()

        # Convert the response into Python data.
        data = response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not retrieve historical weather data: {error}"
        )

    # Open-Meteo stores daily information in parallel arrays.
    daily = data["daily"]

    # Convert the response into a DataFrame.
    weather_df = pd.DataFrame({
        "Date": daily["time"],
        "Temperature_C": daily["temperature_2m_mean"],
        "Rainfall_mm": daily["rain_sum"],
        "Weather_Code": daily["weather_code"]
    })

    # Convert the WMO code into a readable condition.
    weather_df["Weather_Condition"] = (
        weather_df["Weather_Code"]
        .apply(weather_code_to_condition)
    )

    # Make sure Date is stored as a proper datetime value.
    weather_df["Date"] = pd.to_datetime(weather_df["Date"])

    return weather_df


# ============================================================
# TODAY'S WEATHER
# ============================================================

def get_today_weather():
    """
    Retrieve today's weather for the bakery location.

    This is used when storing today's actual bakery data.

    Returns
    -------
    dict
        Dictionary containing today's weather information.
    """

    today = date.today()

    # Request today's weather using the forecast endpoint.
    #
    # The forecast API can also provide recent past days, which
    # makes it useful for obtaining today's observed/recent
    # weather information.
    params = {
        "latitude": BAKERY["latitude"],
        "longitude": BAKERY["longitude"],
        "daily": [
            "temperature_2m_mean",
            "rain_sum",
            "weather_code"
        ],
        "past_days": 1,
        "forecast_days": 1,
        "timezone": "auto",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm"
    }

    try:
        response = requests.get(
            FORECAST_API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not retrieve today's weather: {error}"
        )

    daily = data["daily"]

    # Find today's date inside the returned daily data.
    dates = daily["time"]

    today_string = today.isoformat()

    if today_string not in dates:
        raise RuntimeError(
            "Today's weather was not returned by Open-Meteo."
        )

    index = dates.index(today_string)

    weather_code = daily["weather_code"][index]

    return {
        "Date": today_string,
        "Temperature_C": daily["temperature_2m_mean"][index],
        "Rainfall_mm": daily["rain_sum"][index],
        "Weather_Code": weather_code,
        "Weather_Condition": weather_code_to_condition(
            weather_code
        )
    }


# ============================================================
# TOMORROW'S WEATHER
# ============================================================

def get_tomorrow_weather():
    """
    Retrieve tomorrow's weather forecast for the bakery location.

    This information is used when generating tomorrow's demand
    forecast.

    Returns
    -------
    dict
        Dictionary containing tomorrow's forecast weather.
    """

    tomorrow = date.today() + timedelta(days=1)

    params = {
        "latitude": BAKERY["latitude"],
        "longitude": BAKERY["longitude"],
        "daily": [
            "temperature_2m_mean",
            "rain_sum",
            "weather_code"
        ],
        "forecast_days": 2,
        "timezone": "auto",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm"
    }

    try:
        response = requests.get(
            FORECAST_API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not retrieve tomorrow's weather: {error}"
        )

    daily = data["daily"]

    tomorrow_string = tomorrow.isoformat()

    dates = daily["time"]

    if tomorrow_string not in dates:
        raise RuntimeError(
            "Tomorrow's weather was not returned by Open-Meteo."
        )

    index = dates.index(tomorrow_string)

    weather_code = daily["weather_code"][index]

    return {
        "Date": tomorrow_string,
        "Temperature_C": daily["temperature_2m_mean"][index],
        "Rainfall_mm": daily["rain_sum"][index],
        "Weather_Code": weather_code,
        "Weather_Condition": weather_code_to_condition(
            weather_code
        )
    }