import streamlit as st

from utils.ui import page_header, require_login
from ml.train import train_model

st.set_page_config(page_title="Model Management", layout="wide")

require_login()

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

page_header(
    "Model Management",
    "Monitor forecasting performance and retrain the demand prediction model when needed.",
)

st.divider()

# Current model overview
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
    "Retraining evaluates a candidate model against the current model. "
    "The existing model is retained if the candidate does not perform better."
)

st.divider()

# Dataset information
st.subheader("Training Data")

try:
    from backend.data import load_bakery_data

    df = load_bakery_data()

    if df.empty:
        st.warning("No training data is available.")
    else:
        df["Date"] = __import__("pandas").to_datetime(df["Date"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Training Records", f"{len(df):,}")

        with col2:
            st.metric("First Record", df["Date"].min().strftime("%d %b %Y"))

        with col3:
            st.metric("Latest Record", df["Date"].max().strftime("%d %b %Y"))

except Exception as error:
    st.error("Unable to load training data.")
    st.exception(error)

st.divider()

# Retraining
st.subheader("Retrain Demand Model")
st.write(
    "Retraining can improve forecasts as more sales records become available. "
    "This process may take some time."
)

if st.button("Start Model Training", type="primary", use_container_width=True):
    with st.spinner("Training and evaluating the candidate model... Please wait."):
        try:
            result = train_model()

            st.divider()
            st.subheader("Training Results")

            candidate = result.get("candidate_metrics", {})
            current = result.get("current_metrics", {})

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Candidate Model**")
                if candidate:
                    st.metric(
                        "MAE",
                        f"{candidate.get('MAE', 0):.2f}",
                    )
                    st.metric(
                        "RMSE",
                        f"{candidate.get('RMSE', 0):.2f}",
                    )
                    if "WAPE" in candidate:
                        st.metric(
                            "WAPE",
                            f"{candidate['WAPE']:.2f}%",
                        )
                else:
                    st.write("Candidate metrics are unavailable.")

            with col2:
                st.markdown("**Current Model**")
                if current:
                    st.metric(
                        "MAE",
                        f"{current.get('MAE', 0):.2f}",
                    )
                    st.metric(
                        "RMSE",
                        f"{current.get('RMSE', 0):.2f}",
                    )
                    if "WAPE" in current:
                        st.metric(
                            "WAPE",
                            f"{current['WAPE']:.2f}%",
                        )
                else:
                    st.write("Current metrics are unavailable.")

            st.write(
                f"**Training records:** "
                f"{result.get('training_records', 'Unavailable')}"
            )

            start_date = result.get("training_start_date")
            end_date = result.get("training_end_date")

            if start_date is not None and end_date is not None:
                st.write(f"**Training period:** {start_date} to {end_date}")

            if result.get("replaced_model", False):
                st.success(
                    "The candidate model performed better and has replaced the previous model."
                )
            else:
                st.info(
                    "The current model has been retained because the candidate "
                    "did not outperform it."
                )

        except Exception as error:
            st.error("Model training failed. The current model should remain unchanged.")
            st.exception(error)