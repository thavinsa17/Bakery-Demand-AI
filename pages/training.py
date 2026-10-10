import os
import streamlit as st

from utils.ui import page_header, require_login
from ml.train import train_model, MODEL_PATH, load_data


st.set_page_config(
    page_title="Model Management",
    page_icon="🥐",
    layout="wide",
)

require_login()

page_header(
    "Model Management",
    "View the current forecasting model and manage model training.",
)


# ------------------------------------------------------------
# CURRENT MODEL
# ------------------------------------------------------------

st.subheader("Current Model")

model_exists = os.path.exists(MODEL_PATH)

col1, col2 = st.columns(2)

with col1:
    st.metric("Model Type", "XGBoost")

with col2:
    st.metric(
        "Saved Model",
        "Available" if model_exists else "Not found",
    )

if model_exists:
    st.caption(f"Model file: {MODEL_PATH}")
else:
    st.warning(
        "No saved model was found. A successful training run may "
        "create one if the candidate model can be trained."
    )


# ------------------------------------------------------------
# TRAINING DATASET INFORMATION
# ------------------------------------------------------------

st.subheader("Training Dataset")

try:
    training_data = load_data()

    st.metric(
        "Available Records",
        f"{len(training_data):,}",
    )

    if "Date" in training_data.columns and not training_data.empty:
        st.write(
            f"**Date range:** "
            f"{training_data['Date'].min().date()} to "
            f"{training_data['Date'].max().date()}"
        )

except Exception as error:
    st.error(f"Could not load the training dataset: {error}")
    st.stop()


st.divider()


# ------------------------------------------------------------
# RETRAIN MODEL
# ------------------------------------------------------------

st.subheader("Retrain Model")

st.write(
    "Training uses historical bakery data and evaluates the candidate "
    "model against the current model. The existing model is retained "
    "unless the candidate has a lower MAE."
)

if st.button("Retrain Model", type="primary"):

    try:
        with st.spinner(
            "Training and evaluating the model. This may take several minutes..."
        ):
            results = train_model()

        st.success("Model training and evaluation completed.")

        candidate_metrics = results["candidate_metrics"]
        current_metrics = results["current_metrics"]

        st.subheader("Candidate Model Performance")

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "MAE",
            f"{candidate_metrics['mae']:.2f} units",
        )

        metric2.metric(
            "RMSE",
            f"{candidate_metrics['rmse']:.2f} units",
        )

        metric3.metric(
            "WAPE",
            f"{candidate_metrics['wape'] * 100:.2f}%",
        )

        st.write(
            f"**Training records:** "
            f"{results['training_records']:,}"
        )

        st.write(
            f"**Training data period:** "
            f"{results['training_start_date']} to "
            f"{results['training_end_date']}"
        )

        if results["replaced_model"]:
            st.success(
                "The candidate model was selected and saved as the "
                "new forecasting model."
            )
        else:
            st.info(
                "The existing model was retained because the candidate "
                "did not achieve a lower MAE."
            )

        if current_metrics is not None:
            st.subheader("Model Comparison")

            comparison_data = {
                "Metric": ["MAE", "RMSE", "WAPE"],
                "Current Model": [
                    f"{current_metrics['mae']:.2f}",
                    f"{current_metrics['rmse']:.2f}",
                    f"{current_metrics['wape'] * 100:.2f}%",
                ],
                "Candidate Model": [
                    f"{candidate_metrics['mae']:.2f}",
                    f"{candidate_metrics['rmse']:.2f}",
                    f"{candidate_metrics['wape'] * 100:.2f}%",
                ],
            }

            st.dataframe(
                comparison_data,
                hide_index=True,
                use_container_width=True,
            )

    except Exception as error:
        st.error(
            "Model training failed. Check the terminal for details. "
            f"Error: {error}"
        )