import streamlit as st
import pandas as pd

from utils.ui import page_header, require_login
from backend.data import load_bakery_data
from ml.train import train_model


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Model Management",
    layout="wide",
)

require_login()


# ==================================================
# THEME AND STYLING
# ==================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1250px;
        }

        h1, h2, h3 {
            color: #49352B;
        }

        .section-caption {
            color: #75665C;
            font-size: 0.92rem;
        }

        .metric-card {
            background-color: #EDE3D5;
            border: 1px solid #E1D3C1;
            border-radius: 12px;
            padding: 18px;
            min-height: 115px;
        }

        .metric-label {
            color: #75665C;
            font-size: 0.88rem;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #49352B;
            font-size: 1.8rem;
            font-weight: 700;
        }

        .metric-description {
            color: #75665C;
            font-size: 0.8rem;
            margin-top: 5px;
        }

        .status-card {
            background-color: #F7F1E7;
            border-left: 4px solid #A95137;
            border-radius: 7px;
            padding: 15px 18px;
            margin: 12px 0 20px 0;
        }

        div.stButton > button {
            background-color: #A95137;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.65rem 1rem;
            font-weight: 600;
        }

        div.stButton > button:hover {
            background-color: #8F422D;
            color: white;
        }

        div[data-testid="stMetric"] {
            background-color: #EDE3D5;
            border: 1px solid #E1D3C1;
            padding: 14px;
            border-radius: 10px;
        }

        hr {
            border-color: #E1D3C1;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def get_metric(metrics, key):
    """Return a metric value safely."""

    if not isinstance(metrics, dict):
        return None

    value = metrics.get(key)

    if value is None:
        return None

    try:
        value = float(value)

        if pd.isna(value):
            return None

        return value

    except (TypeError, ValueError):
        return None


def format_number(value, decimals=2):
    """Format a numeric value for display."""

    if value is None:
        return "N/A"

    return f"{value:,.{decimals}f}"


def format_percentage(value):
    """Convert a WAPE ratio to a percentage for display."""

    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


def calculate_change(current_value, candidate_value):
    """
    Calculate percentage change relative to the current model.

    Negative means the candidate error decreased.
    Positive means the candidate error increased.
    """

    if current_value is None or candidate_value is None:
        return None

    if current_value == 0:
        return None

    return (
        (candidate_value - current_value)
        / abs(current_value)
    ) * 100


def render_metric_card(label, value, description):
    """Render a consistently styled metric card."""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# PAGE HEADER
# ==================================================

page_header(
    "Model Management",
    "Train, evaluate, and compare bakery demand forecasting models.",
)


# ==================================================
# DATASET OVERVIEW
# ==================================================

st.subheader("Training Dataset")

try:
    bakery_data = load_bakery_data()

    if bakery_data is not None and not bakery_data.empty:

        dataset_col1, dataset_col2, dataset_col3 = st.columns(3)

        with dataset_col1:
            st.metric(
                "Training Records",
                f"{len(bakery_data):,}",
            )

        with dataset_col2:
            if "Date" in bakery_data.columns:
                dates = pd.to_datetime(
                    bakery_data["Date"],
                    errors="coerce",
                ).dropna()

                if not dates.empty:
                    date_range = (
                        f"{dates.min().strftime('%d %b %Y')} – "
                        f"{dates.max().strftime('%d %b %Y')}"
                    )
                else:
                    date_range = "Unavailable"
            else:
                date_range = "Unavailable"

            st.metric("Data Coverage", date_range)

        with dataset_col3:
            product_count = (
                bakery_data["Product"].nunique()
                if "Product" in bakery_data.columns
                else 0
            )

            st.metric(
                "Bakery Products",
                f"{product_count:,}",
            )

    else:
        st.warning(
            "The training dataset is empty. Add bakery sales data "
            "before training the model."
        )

except Exception as error:
    st.warning("Unable to load the training dataset overview.")

    with st.expander("View details"):
        st.exception(error)


st.divider()


# ==================================================
# MODEL OVERVIEW
# ==================================================

st.subheader("Model Overview")

current_col, candidate_col = st.columns(2)

with current_col:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">CURRENT MODEL</div>
            <div style="font-size: 1.15rem; font-weight: 700;
                        color: #49352B;">
                Active Forecasting Model
            </div>
            <div class="metric-description">
                The model currently used to generate demand forecasts.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with candidate_col:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">CANDIDATE MODEL</div>
            <div style="font-size: 1.15rem; font-weight: 700;
                        color: #49352B;">
                Newly Trained Model
            </div>
            <div class="metric-description">
                Evaluated against the current model before replacement.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# TRAINING CONTROLS
# ==================================================

st.divider()

st.subheader("Train Model")

st.markdown(
    """
    Train a new candidate model using the available bakery sales data.
    The application compares its performance with the current model
    and replaces the current model only when the candidate achieves
    a lower MAE.
    """
)

train_col, info_col = st.columns([1, 2])

with train_col:
    start_training = st.button(
        "Train New Model",
        use_container_width=True,
    )

with info_col:
    st.caption(
        "Training can take several minutes while the model evaluates "
        "different parameter combinations."
    )


# ==================================================
# RUN TRAINING
# ==================================================

if start_training:

    try:
        with st.spinner(
            "Training and evaluating the candidate model..."
        ):
            result = train_model()

        st.session_state["training_result"] = result
        st.session_state["training_error"] = None

        st.success("Training process completed.")

    except Exception as error:
        st.session_state["training_error"] = str(error)

        st.error("Model training failed.")

        with st.expander("View training error", expanded=True):
            st.exception(error)


# ==================================================
# DISPLAY TRAINING RESULTS
# ==================================================

training_result = st.session_state.get("training_result")
training_error = st.session_state.get("training_error")


if training_error:
    st.warning(
        "The latest training attempt failed. "
        "Any results below are from the last successful training run."
    )


if not training_result:

    st.info(
        "Train a candidate model to see its performance comparison here."
    )

else:

    current_metrics = training_result.get("current_metrics")
    candidate_metrics = training_result.get("candidate_metrics")

    replaced_model = training_result.get("replaced_model", False)

    st.divider()

    st.subheader("Latest Training Results")

    # --------------------------------------------------
    # TRAINING STATUS
    # --------------------------------------------------

    if replaced_model and current_metrics is None:

        st.success(
            "The first model was trained and saved successfully."
        )

    elif replaced_model:

        st.success(
            "The candidate model achieved a lower MAE and replaced "
            "the previous model."
        )

    else:

        st.info(
            "The candidate model did not achieve a lower MAE. "
            "The existing model was retained."
        )

    # --------------------------------------------------
    # TRAINING DETAILS
    # --------------------------------------------------

    with st.expander("Training details"):

        detail_col1, detail_col2, detail_col3 = st.columns(3)

        with detail_col1:
            st.metric(
                "Records Used",
                f"{training_result.get('training_records', 0):,}",
            )

        with detail_col2:
            st.metric(
                "Training Start",
                training_result.get(
                    "training_start_date",
                    "N/A",
                ),
            )

        with detail_col3:
            st.metric(
                "Training End",
                training_result.get(
                    "training_end_date",
                    "N/A",
                ),
            )

    # --------------------------------------------------
    # METRIC VALUES
    # --------------------------------------------------

    st.subheader("Model Performance")

    st.markdown(
        '<p class="section-caption">'
        "Compare the prediction errors of the current and candidate models."
        "</p>",
        unsafe_allow_html=True,
    )

    current_mae = get_metric(current_metrics, "mae")
    candidate_mae = get_metric(candidate_metrics, "mae")

    current_rmse = get_metric(current_metrics, "rmse")
    candidate_rmse = get_metric(candidate_metrics, "rmse")

    current_wape = get_metric(current_metrics, "wape")
    candidate_wape = get_metric(candidate_metrics, "wape")

    # Three compact cards instead of three large charts.
    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        render_metric_card(
            "Candidate MAE",
            format_number(candidate_mae),
            "Average absolute error in units sold",
        )

    with metric_col2:
        render_metric_card(
            "Candidate RMSE",
            format_number(candidate_rmse),
            "Penalises larger prediction errors",
        )

    with metric_col3:
        render_metric_card(
            "Candidate WAPE",
            format_percentage(candidate_wape),
            "Weighted percentage error",
        )

    st.write("")

    # --------------------------------------------------
    # SINGLE COMPARISON CHART
    # --------------------------------------------------

    st.subheader("Relative Error Comparison")

    st.markdown(
        """
        <p class="section-caption">
            Percentage change in prediction error compared with the current
            model. Negative values indicate improvement; positive values
            indicate higher error.
        </p>
        """,
        unsafe_allow_html=True,
    )

    comparison_rows = []

    metric_comparisons = [
        ("MAE", current_mae, candidate_mae),
        ("RMSE", current_rmse, candidate_rmse),
        ("WAPE", current_wape, candidate_wape),
    ]

    for metric_name, current_value, candidate_value in metric_comparisons:

        change = calculate_change(
            current_value,
            candidate_value,
        )

        if change is not None:

            comparison_rows.append(
                {
                    "Metric": metric_name,
                    "Current Model": 0.0,
                    "Candidate Model": change,
                }
            )

    if comparison_rows:

        comparison_df = pd.DataFrame(comparison_rows)

        st.caption(
            "The current model is the 0% baseline. "
            "All three metrics are expressed as percentage change, "
            "so they can be compared on one chart."
        )

        chart_df = comparison_df.set_index("Metric")

        st.bar_chart(
            chart_df,
            horizontal=True,
            use_container_width=True,
        )

        # --------------------------------------------------
        # TEXT SUMMARY
        # --------------------------------------------------

        st.markdown("#### Metric-by-metric results")

        for metric_name, current_value, candidate_value in metric_comparisons:

            change = calculate_change(
                current_value,
                candidate_value,
            )

            if change is None:
                st.write(
                    f"**{metric_name}:** Comparison unavailable "
                    "because the current value is missing or zero."
                )

            elif change < 0:
                st.write(
                    f"**{metric_name}:** Error decreased by "
                    f"{abs(change):.2f}%."
                )

            elif change > 0:
                st.write(
                    f"**{metric_name}:** Error increased by "
                    f"{change:.2f}%."
                )

            else:
                st.write(
                    f"**{metric_name}:** No change in error."
                )

    else:

        st.info(
            "A relative comparison chart will appear after both the "
            "current and candidate model metrics are available."
        )

    # --------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------

    st.divider()

    with st.expander("How to read these results"):

        st.markdown(
            """
            - **MAE:** The average absolute difference between predicted
              and actual sales, measured in units sold.
            - **RMSE:** Gives greater weight to larger prediction errors.
            - **WAPE:** Measures absolute prediction error relative to
              total actual sales.
            - **Negative percentage change:** The candidate model has
              lower error than the current model.
            - **Positive percentage change:** The candidate model has
              higher error than the current model.
            - **Model replacement:** The application uses MAE to decide
              whether to replace the current model.
            """
        )

    st.caption(
        "Results remain available in the current Streamlit session. "
        "They may be cleared when the session resets or the app restarts."
    )