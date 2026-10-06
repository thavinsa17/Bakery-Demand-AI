"""
ml/train.py

Handles model training and retraining for the bakery demand
forecasting application.

The model-development process follows the same steps used in
02_model_development.ipynb.
"""

# ============================================================
# IMPORT LIBRARIES
# ============================================================

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "bakery_data.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "demand_model.pkl")


# ============================================================
# MODEL CONFIGURATION
# ============================================================

TARGET = "Units_Sold"

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

CATEGORICAL_FEATURES = [
    "Product",
    "Day_of_Week",
    "Season",
    "Weather_Condition"
]

NUMERICAL_FEATURES = [
    "Month",
    "Is_Weekend",
    "Temperature_C",
    "Rainfall_mm",
    "Is_Holiday",
    "Day_Before_Holiday",
    "Day_After_Holiday",
    "Base_Price_LKR"
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """Load the live bakery dataset."""

    print("Loading bakery dataset...")

    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    print(f"Rows: {len(df)} | Columns: {len(df.columns)}")

    return df


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(df):
    """Create the same chronological train/test split as the notebook."""

    df = df.sort_values(["Date", "Product"]).reset_index(drop=True)

    missing_features = [column for column in FEATURES if column not in df.columns]

    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")

    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' is missing.")

    unique_dates = sorted(df["Date"].unique())
    split_index = int(len(unique_dates) * 0.80)

    train_dates = unique_dates[:split_index]
    test_dates = unique_dates[split_index:]

    train_df = df[df["Date"].isin(train_dates)].copy()
    test_df = df[df["Date"].isin(test_dates)].copy()

    X_train = train_df[FEATURES].copy()
    y_train = train_df[TARGET].copy()

    X_test = test_df[FEATURES].copy()
    y_test = test_df[TARGET].copy()

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")
    print(f"Training period: {train_df['Date'].min().date()} to {train_df['Date'].max().date()}")
    print(f"Testing period: {test_df['Date'].min().date()} to {test_df['Date'].max().date()}")

    return X_train, X_test, y_train, y_test


# ============================================================
# CREATE PREPROCESSOR
# ============================================================

def create_preprocessor():
    """Create the same preprocessing used in the notebook."""

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("numerical", "passthrough", NUMERICAL_FEATURES)
        ]
    )

    return preprocessor


# ============================================================
# HYPERPARAMETER TUNING
# ============================================================

def tune_model(X_train, y_train, preprocessor):
    """
    Tune XGBoost using the same procedure as the notebook.

    Preprocessing is fitted on X_train first.
    RandomizedSearchCV then works on the processed training data.
    """

    print("")
    print("Starting preprocessing...")

    X_train_processed = preprocessor.fit_transform(X_train)

    print("Training data preprocessing completed.")

    base_xgb = XGBRegressor(
        objective="reg:squarederror",
        random_state=42
    )

    param_distributions = {
        "n_estimators": [100, 200, 300, 400, 500, 600],
        "learning_rate": [0.01, 0.03, 0.05, 0.07, 0.1],
        "max_depth": [3, 4, 5, 6, 7, 8],
        "min_child_weight": [1, 3, 5, 7],
        "subsample": [0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
        "gamma": [0, 0.1, 0.2, 0.3]
    }

    time_series_cv = TimeSeriesSplit(n_splits=4)

    random_search = RandomizedSearchCV(
        estimator=base_xgb,
        param_distributions=param_distributions,
        n_iter=30,
        scoring="neg_mean_absolute_error",
        cv=time_series_cv,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )

    print("")
    print("Starting hyperparameter tuning...")

    random_search.fit(X_train_processed, y_train)

    print("")
    print("Best parameters:")

    for parameter, value in random_search.best_params_.items():
        print(f"{parameter}: {value}")

    print(f"Best CV MAE: {-random_search.best_score_:.4f}")

    return random_search.best_params_


# ============================================================
# CREATE FINAL PIPELINE
# ============================================================

def create_final_pipeline(best_params):
    """
    Create the same final pipeline used in the notebook.
    """

    preprocessor = create_preprocessor()

    final_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", XGBRegressor(
                **best_params,
                objective="reg:squarederror",
                random_state=42
            ))
        ]
    )

    return final_pipeline


# ============================================================
# CALCULATE WAPE
# ============================================================

def calculate_wape(actual, predicted):
    """Calculate Weighted Absolute Percentage Error."""

    actual = np.asarray(actual)
    predicted = np.asarray(predicted)

    denominator = np.sum(np.abs(actual))

    if denominator == 0:
        return 0.0

    return np.sum(np.abs(actual - predicted)) / denominator


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model(model, X_test, y_test):
    """Evaluate a model using MAE, RMSE and WAPE."""

    predictions = model.predict(X_test)
    predictions = np.maximum(predictions, 0)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    wape = calculate_wape(y_test, predictions)

    return {
        "mae": mae,
        "rmse": rmse,
        "wape": wape
    }


# ============================================================
# LOAD CURRENT MODEL
# ============================================================

def load_current_model():
    """Load the currently saved model."""

    if not os.path.exists(MODEL_PATH):
        print("No existing model found.")
        return None

    current_model = joblib.load(MODEL_PATH)

    print("Current model loaded successfully.")

    return current_model


# ============================================================
# COMPARE MODELS
# ============================================================

def compare_models(current_model, candidate_model, X_test, y_test):
    """
    Compare the candidate model with the currently saved model.

    The candidate replaces the current model only when its MAE
    is lower.
    """

    candidate_metrics = evaluate_model(
        candidate_model,
        X_test,
        y_test
    )

    print("")
    print("Candidate model evaluation")
    print("--------------------------")
    print(f"MAE: {candidate_metrics['mae']:.2f} units")
    print(f"RMSE: {candidate_metrics['rmse']:.2f} units")
    print(f"WAPE: {candidate_metrics['wape'] * 100:.2f}%")

    if current_model is None:
        return True, candidate_metrics, None

    current_metrics = evaluate_model(
        current_model,
        X_test,
        y_test
    )

    print("")
    print("Current model evaluation")
    print("------------------------")
    print(f"MAE: {current_metrics['mae']:.2f} units")
    print(f"RMSE: {current_metrics['rmse']:.2f} units")
    print(f"WAPE: {current_metrics['wape'] * 100:.2f}%")

    replace_model = candidate_metrics["mae"] < current_metrics["mae"]

    return replace_model, candidate_metrics, current_metrics


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(model):
    """Save the selected model."""

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print("")
    print("Model saved successfully.")
    print(f"Model path: {MODEL_PATH}")


# ============================================================
# MAIN TRAINING FUNCTION
# ============================================================

def train_model():
    """Run the complete model training and selection process."""

    print("")
    print("==============================")
    print("BAKERY DEMAND MODEL TRAINING")
    print("==============================")
    print("")

    df = load_data()

    X_train, X_test, y_train, y_test = prepare_data(df)

    preprocessor = create_preprocessor()

    best_params = tune_model(
        X_train,
        y_train,
        preprocessor
    )

    candidate_model = create_final_pipeline(best_params)

    print("")
    print("Training final model...")

    candidate_model.fit(X_train, y_train)

    print("Final model training completed.")

    current_model = load_current_model()

    replace_model, candidate_metrics, current_metrics = compare_models(
        current_model,
        candidate_model,
        X_test,
        y_test
    )

    print("")

    if replace_model:
        save_model(candidate_model)
        print("Candidate model is better.")
        print("The saved model has been replaced.")
    else:
        print("Candidate model is not better.")
        print("The current model has been kept.")

    print("")
    print("==============================")
    print("TRAINING COMPLETE")
    print("==============================")

    return candidate_metrics, current_metrics


# ============================================================
# RUN TRAINING
# ============================================================

if __name__ == "__main__":
    train_model()