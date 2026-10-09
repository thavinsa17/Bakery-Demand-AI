
# ml/predict.py

# ============================================================
# IMPORT LIBRARIES
# ============================================================

import os
import joblib
import pandas as pd


# ============================================================
# MODEL CONFIGURATION
# ============================================================

# Build the path to the trained model file.
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "demand_model.pkl"
)


# ============================================================
# MODEL FEATURES
# ============================================================

# These are the 12 features expected by the trained model.
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


# ============================================================
# MODEL LOADING AND RELOADING
# ============================================================

# Keep the currently loaded model in memory.
_model = None

# Remember the last modification time of the model file.
_model_mtime = None


def load_model():
    """
    Load the trained model when necessary.

    If the model file changes after retraining, load the new
    model instead of continuing to use the old model in memory.
    """

    global _model, _model_mtime

    # Ensure that the model file exists.
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}"
        )

    # Read the current modification time of the model file.
    current_mtime = os.path.getmtime(MODEL_PATH)

    # Load or reload the model if it has not been loaded yet,
    # or if the model file has changed.
    if _model is None or current_mtime != _model_mtime:
        _model = joblib.load(MODEL_PATH)
        _model_mtime = current_mtime

        print("Demand model loaded or refreshed successfully.")

    return _model


# ============================================================
# FORCE MODEL RELOAD
# ============================================================

def reload_model():
    """
    Force the prediction module to load the latest saved model.

    Call this after retraining finishes and the new model
    has been saved successfully.
    """

    global _model, _model_mtime

    # Clear the cached model and its saved modification time.
    _model = None
    _model_mtime = None

    # Load the current model file immediately.
    return load_model()


# ============================================================
# PREDICT DEMAND FOR ONE PRODUCT
# ============================================================

def predict_product_demand(product_data):
    """
    Predict demand for one bakery product.

    Parameters
    ----------
    product_data : dict
        Must contain all 12 features expected by the model.

    Returns
    -------
    int
        Predicted demand, rounded to a whole unit and never
        below zero.
    """

    # Check that every required feature is present.
    missing_features = [
        feature for feature in FEATURES
        if feature not in product_data
    ]

    if missing_features:
        raise ValueError(
            f"Missing prediction features: {missing_features}"
        )

    # Arrange the input columns in the exact training order.
    input_data = pd.DataFrame(
        [product_data],
        columns=FEATURES
    )

    # Obtain the current model, reloading it if it has changed.
    model = load_model()

    # Generate the prediction.
    prediction = model.predict(input_data)[0]

    # Convert the result into a non-negative whole number.
    prediction = max(0, round(prediction))

    return prediction


# ============================================================
# MANUAL TEST
# ============================================================

# Run this sample only when this file is executed directly.
# Importing this module from another file will not run the test.

if __name__ == "__main__":

    # Example input containing all 12 required model features.
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

    # Predict demand using the currently saved model.
    sample_prediction = predict_product_demand(sample_product)

    # Display the result.
    print("Prediction features configured.")
    print("Number of features:", len(FEATURES))
    print("Sample prediction:")
    print("Chicken Bun:", sample_prediction, "units")
