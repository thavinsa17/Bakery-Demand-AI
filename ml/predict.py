# ml/predict.py

# Import libraries
import joblib
import pandas as pd
import os

# Model file location
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "demand_model.pkl")

# Load the trained model
model = joblib.load(MODEL_PATH)

print("Demand model loaded successfully.")

# Features expected by the trained model
FEATURES = [
    "Product",
    "Day_of_Week",
    "Month",
    "Season",
    "Is_Weekend",
    "Temperature_C",
    "Rainfall_mm",
    "Weather_Condition",
    "Is_Holiday",
    "Day_Before_Holiday",
    "Day_After_Holiday",
    "Base_Price_LKR"
]

print("Prediction features configured.")
print("Number of features:", len(FEATURES))

# Predict demand for one product
def predict_product_demand(product_data):
    """
    Predict demand for one bakery product.

    product_data should contain all 12 model features.
    """

    input_data = pd.DataFrame([product_data],columns=FEATURES)
    prediction = model.predict(input_data)[0]
    prediction = max(0, round(prediction))
    return prediction


# Test the prediction function
sample_product = {
    "Product": "Chicken Bun",
    "Day_of_Week": "Wednesday",
    "Month": 10,
    "Season": "Second Inter-monsoon",
    "Is_Weekend": False,
    "Temperature_C": 24.5,
    "Rainfall_mm": 4.2,
    "Weather_Condition": "Rain",
    "Is_Holiday": False,
    "Day_Before_Holiday": False,
    "Day_After_Holiday": False,
    "Base_Price_LKR": 100
}

sample_prediction = predict_product_demand(sample_product)

print("Sample prediction:")
print("Chicken Bun:", sample_prediction, "units")