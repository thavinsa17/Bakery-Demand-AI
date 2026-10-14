
import streamlit as st
import pandas as pd

from utils.ui import page_header, require_login
from ml.train import train_model


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Model Management | BakeWise",
    layout="wide",
)

require_login()


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .model-card {
        background-color: #FFFFFF;
        border: 1px solid #E5D7C7;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .model-label {
        color: #806B5B;
        font-size: 0.85rem;
        margin-bottom: 6px;
    }

    .model-value {
        color: #49352B;
        font-size: 1.15rem;
        font-weight: 600;
    }

    div.stButton > button {
        border-radius: 8px;
        min-height: 44px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "Model Management",
    "Monitor forecasting performance and retrain the demand "
    "prediction model when needed.",
)

st.divider()


# ============================================================
# CURRENT MODEL OVERVIEW
# ============================================================

st.subheader("Current Model")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="model-card">
            <div class="model-label">Model Type</div>
            <div class="model-value">XGBoost Regressor</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="model-card">
            <div class="model-label">Model Status</div>
            <div class="model-value">Ready for Predictions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info(
    "Retraining evaluates a candidate model against the current "
    "model using the same test data. The existing model is retained "
    "if the candidate does not perform better."
)

st.divider()


# ============================================================
# TRAINING DATA INFORMATION
# ============================================================

st.subheader("Training Data")

try:
    from backend.data import load_bakery_data

    df = load_bakery_data()

    if df.empty:
        st.warning("No training data is available.")

    elif "Date" not in df.columns:
        st.error("The training dataset does not contain a Date column.")

    else:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        valid_dates = df["Date"].dropna()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Training Records",
                f"{len(df):,}",
            )

        with col2:
            if not valid_dates.empty:
                st.metric(
                    "First Record",
                    valid_dates.min().strftime("%d %b %Y"),
                )
            else:
                st.metric("First Record", "Unavailable")

        with col3:
            if not valid_dates.empty:
                st.metric(
                    "Latest Record",
                    valid_dates.max().strftime("%d %b %Y"),
                )
            else:
                st.metric("Latest Record", "Unavailable")

except Exception as error:
    st.error("Unable to load training data.")
    with st.expander("View error details"):
        st.exception(error)


st.divider()


# ============================================================
# RETRAIN DEMAND MODEL
# ============================================================

st.subheader("Retrain Demand Model")

st.write(
    "Retraining uses the latest available bakery data to train "
    "and evaluate a candidate forecasting model. The candidate "
    "replaces the existing model only if it performs better."
)

if st.button(
    "Start Model Training",
    type="primary",
    use_container_width=True,
):

    with st.spinner(
        "Training and evaluating the candidate model... Please wait."
    ):
        try:
            result = train_model()

            # ------------------------------------------------
            # EXTRACT RESULTS
            # ------------------------------------------------

            candidate = result.get("candidate_metrics") or {}
            current = result.get("current_metrics") or {}

            st.divider()
            st.subheader("Training Results")

            # ------------------------------------------------
            # CANDIDATE MODEL METRICS
            # Metric keys from ml.train are lowercase:
            # mae, rmse, wape.
            # ------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Candidate Model")

                if candidate:
                    if candidate.get("mae") is not None:
                        st.metric(
                            "MAE",
                            f"{candidate['mae']:.2f} units",
                            help=(
                                "Mean Absolute Error: the average "
                                "absolute difference between actual "
                                "and predicted demand."
                            ),
                        )
                    else:
                        st.metric("MAE", "Unavailable")

                    if candidate.get("rmse") is not None:
                        st.metric(
                            "RMSE",
                            f"{candidate['rmse']:.2f} units",
                            help=(
                                "Root Mean Squared Error: a metric "
                                "that penalizes larger prediction "
                                "errors more heavily."
                            ),
                        )
                    else:
                        st.metric("RMSE", "Unavailable")

                    if candidate.get("wape") is not None:
                        st.metric(
                            "WAPE",
                            f"{candidate['wape'] * 100:.2f}%",
                            help=(
                                "Weighted Absolute Percentage Error: "
                                "total absolute prediction error "
                                "divided by total actual demand."
                            ),
                        )
                    else:
                        st.metric("WAPE", "Unavailable")

                else:
                    st.warning(
                        "Candidate model metrics are unavailable."
                    )

            # ------------------------------------------------
            # CURRENT MODEL METRICS
            # ------------------------------------------------

            with col2:
                st.markdown("### Current Model")

                if current:
                    if current.get("mae") is not None:
                        st.metric(
                            "MAE",
                            f"{current['mae']:.2f} units",
                        )
                    else:
                        st.metric("MAE", "Unavailable")

                    if current.get("rmse") is not None:
                        st.metric(
                            "RMSE",
                            f"{current['rmse']:.2f} units",
                        )
                    else:
                        st.metric("RMSE", "Unavailable")

                    if current.get("wape") is not None:
                        st.metric(
                            "WAPE",
                            f"{current['wape'] * 100:.2f}%",
                        )
                    else:
                        st.metric("WAPE", "Unavailable")

                else:
                    st.info(
                        "No current model metrics were returned. "
                        "This can happen when no previous model "
                        "was available for comparison."
                    )

            # ------------------------------------------------
            # TRAINING DATA SUMMARY
            # ------------------------------------------------

            st.divider()
            st.subheader("Training Summary")

            summary_col1, summary_col2 = st.columns(2)

            with summary_col1:
                st.write("**Training records**")

                records = result.get("training_records")

                if records is not None:
                    st.write(f"{records:,}")
                else:
                    st.write("Unavailable")

            with summary_col2:
                st.write("**Training period**")

                start_date = result.get("training_start_date")
                end_date = result.get("training_end_date")

                if start_date is not None and end_date is not None:
                    st.write(f"{start_date} to {end_date}")
                else:
                    st.write("Unavailable")

            # ------------------------------------------------
            # MODEL SELECTION RESULT
            # ------------------------------------------------

            st.divider()

            if result.get("replaced_model", False):
                st.success(
                    "The candidate model performed better and "
                    "has replaced the previous model."
                )

            elif current:
                st.info(
                    "The current model has been retained because "
                    "the candidate did not outperform it."
                )

            else:
                st.info(
                    "The training process completed, but no current "
                    "model metrics were available for comparison. "
                    "Check the training logs to confirm which model "
                    "is now being used."
                )

        except Exception as error:
            st.error(
                "Model training failed. The current model should "
                "remain unchanged."
            )

            with st.expander("View error details"):
                st.exception(error)
