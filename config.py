"""
config.py

Stores the fixed configuration for the bakery.

This file contains information that identifies the bakery and its
physical location. Product information and prices are NOT stored here;
those are managed through the live bakery_data.csv file.

The latitude and longitude are especially important because they are
used by the weather module to request weather information for the
bakery's location.
"""

# ============================================================
# BAKERY CONFIGURATION
# ============================================================

BAKERY = {
    # Unique identifier for the bakery.
    # This can be useful if the system is expanded to support multiple bakeries in the future.
    "id": "KB001",
    "name": "Kandy Bakery",
    "city": "Kandy",
    "province": "Central",
    # Address can be used to determine the latitude and longitude adding another layer.
    # Therefore for simplicity we explicity define the latitude and logitude.
    "address": "DUMMY ADDRESS", 
    # Geographic coordinates of the bakery. These are used when requesting weather information.
    "latitude": 7.2906,
    "longitude": 80.6337,
}