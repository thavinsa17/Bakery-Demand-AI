# Bakery Demand AI

*Turning bakery data into better production decisions.*

Bakery Demand AI is a data-driven demand forecasting application designed to help bakeries make more informed daily production decisions. By combining historical sales data with product pricing, weather conditions, and calendar patterns, it estimates how much of each product customers are likely to buy.

Rather than relying solely on intuition or past experience, the system uses machine learning to identify patterns in demand and provide forecasts that can guide production planning. The goal is to help bakeries balance product availability with the cost of producing more than customers need, reducing avoidable waste while protecting potential sales.

## The Problem

Daily production planning requires bakeries to estimate customer demand before actual sales are known. Producing too much can leave unsold products at the end of the day, while producing too little can leave demand unmet. Both outcomes make it difficult to balance product availability with efficient use of ingredients, labour, and other resources.

These decisions become more challenging when demand varies across products and days. Historical sales provide useful evidence, but relying on intuition or past sales alone may not account for factors such as product pricing, weather conditions, weekdays, and public holidays. Without a structured way to consider these factors alongside previous performance, production decisions can be difficult to adapt to changing conditions.

## Our Approach

Bakery Demand AI brings demand forecasting and everyday bakery record-keeping into a single application. It uses historical sales data alongside product prices, weather conditions, and calendar features to estimate demand for individual bakery products.

The application complements these forecasts with tools for recording daily production and sales, tracking leftover quantities, and maintaining product price history. Together, these capabilities provide a more structured view of expected demand and actual outcomes, helping bakery operators make better-informed production decisions and learn from their sales history.

Rather than automatically deciding how much a bakery should produce, Bakery Demand AI is designed to provide data-driven estimates and practical information that support the operator's own planning decisions.

## Features and User Workflow

Bakery Demand AI brings demand forecasting and daily bakery record-keeping together in one Streamlit application. Its workflow connects expected demand with actual production and sales, giving bakery operators information they can use when planning and reviewing their operations.

### 1. Forecast Tomorrow's Demand

The forecasting page generates next-day demand estimates for individual bakery products using a trained XGBoost model. Predictions use historical sales patterns alongside product prices, weather information, and calendar features to estimate the number of units likely to be sold.

### 2. Account for Weather and Calendar Patterns

The forecasting pipeline uses the `requests` library to retrieve weather data from the Open-Meteo API and the `holidays` Python library to identify Sri Lankan public holidays. Using these alongside Python's date and calendar processing capabilities, the system derives features such as the day of the week, month, season, and proximity to public holidays. These features are passed to the trained model together with historical sales and product pricing data to generate demand estimates.

### 3. Record Daily Production and Sales

The daily entries page allows users to record how many units of each product were produced and sold on a given date. These records provide a structured history of bakery operations and help connect forecasted demand with actual sales outcomes.

### 4. Track Leftover Products

Using the recorded production and sales quantities, the application calculates leftover units. This gives users a way to review unsold products and consider how production quantities relate to actual demand.

### 5. Maintain Product Price History

The application supports recording product prices with effective dates. This price history helps the forecasting pipeline select the applicable price for a forecast date, allowing price information to be incorporated into demand estimates.

### 6. Manage the Forecasting Model

The model management page provides information about the available training data and supports retraining and evaluating the demand forecasting model. When new daily production and sales records are added, they can become part of the dataset used for subsequent model training. The training process builds a candidate XGBoost model using the available dataset, evaluates its performance against the current model, and replaces the existing model only when the candidate performs better. This allows the forecasting model to incorporate newly collected operational data over time, provided the dataset is updated and the retraining process completes successfully.

### 7. View Bakery Profile Information

A dedicated profile page presents bakery information and product pricing. The current profile fields are primarily interface-level functionality; changes to the bakery's name, location, contact number, and coordinates are not persisted by the inspected implementation.

### A Typical Workflow

1. **Plan for the next day:** At the end of the working day, review the next-day demand forecasts generated using historical sales, product prices, weather data retrieved through Open-Meteo, and calendar features. Use these estimates to plan the quantities of each product to prepare for the following day.

2. **Prepare and sell products:** Use the forecast as a guide when preparing products for the next working day. Throughout the day, products are sold according to customer demand and normal bakery operations.

3. **Record the day's results:** At the end of the following working day, enter the quantities produced and sold for each product in the daily entries page. The application calculates the leftover quantity for each product, providing a record of the day's unsold stock.

4. **Maintain product prices:** Update product prices when they change, recording their effective dates so the forecasting pipeline can use the appropriate prices for relevant forecast dates.

5. **Improve future forecasts:** As daily production and sales records accumulate, incorporate the updated data into the prepared training dataset and retrain the model through the model management page. The candidate model is evaluated against the existing model before replacement, allowing newly collected data to contribute to future forecasts when retraining is successful.

The application provides forecasts and operational records to support decision-making; it does not automatically determine or enforce production quantities.

## How the System Works

Bakery Demand AI is built around a Streamlit application, a set of Python modules that handle data processing and forecasting, and CSV files that store the bakery's operational records. These components work together to turn historical sales data and daily entries into demand estimates for upcoming production planning.

### 1. Application Architecture

The application is organized into three main layers:

- **User interface (`app.py` and `pages/`)** — Provides the Streamlit home page and the interfaces for signing in, viewing demand forecasts, recording daily production and sales, managing the bakery profile, and retraining the model.
- **Backend (`backend/`)** — Handles bakery data operations, product prices, weather retrieval, holiday information, and forecast generation.
- **Machine learning (`ml/` and `models/`)** — Prepares training data, trains and evaluates the demand prediction model, and loads the saved model to generate predictions.

The `config.py` file stores fixed bakery configuration, including the geographical coordinates used when retrieving weather information. The `utils/` directory contains shared application utilities.

### 2. Data Initialization and Enrichment

The system begins with `data/kandy_bakery_sales_2024_2025.csv`, the original historical sales dataset. It contains records of production and sales, including the date, product, base price, units produced, and units sold. This source file is kept separate from the operational dataset and is not modified by the application.

The initialization script, `setup/initialize_data.py`, reads the original dataset and prepares it for forecasting. It calculates leftover quantities, derives calendar features such as the day of the week, month, season, and weekend status, and adds historical weather and Sri Lankan public-holiday information.

Weather data is retrieved through the Open-Meteo historical weather API, accessed using Python's `requests` library. The `holidays` library supplies Sri Lankan holiday information, including whether a date is a holiday and whether it falls immediately before or after one.

The enriched dataset is saved as `data/bakery_data.csv`. This file becomes the main operational dataset and the source of data for model training. The initialization script is intended to be run once to create the initial dataset from the original historical records.

**Dataset note:** The original `kandy_bakery_sales_2024_2025.csv` dataset was generated using ChatGPT and contains entirely synthetic data. It is used to demonstrate the application's data-processing, feature-engineering, and demand-forecasting workflow. Although historical weather information and calendar features are incorporated during initialization, the underlying production and sales records do not represent verified real-world bakery transactions.

### 3. Data Storage and Daily Operations

The application uses separate CSV files for different types of information:

| File | Purpose |
|---|---|
| `kandy_bakery_sales_2024_2025.csv` | Original historical production and sales data used during initialization. |
| `bakery_data.csv` | Main operational dataset containing historical records and newly submitted daily production and sales entries, together with their associated features. |
| `price_history.csv` | Stores product prices with effective dates, preserving earlier price records when prices change. |
| `forecast_history.csv` | Stores predicted demand by product and forecast date, allowing saved predictions to be retrieved later. |
| `users.csv` | Stores account information used by the application's registration and sign-in functions. |

The `backend/data.py` module handles the operational data files. When a user records daily production and sales, the application validates the quantities, checks for an existing record for the same product and date, calculates leftovers, and adds the new record to `bakery_data.csv`. It also attaches the relevant calendar, weather, holiday, and product-price information.

The application prevents negative production or sales quantities and does not allow units sold to exceed units produced. A product can only have one daily record for a given date.

Product prices are maintained separately from sales records. When a price is updated, the application records the new price and its effective date in `price_history.csv` rather than rewriting earlier sales records. During forecasting, the system selects the latest price effective on or before the forecast date.

Forecasts are stored separately in `forecast_history.csv`. The application can retrieve the saved prediction for a particular product and date, which allows the daily-entry page to display the forecast associated with that day's records. Saving a new forecast for the same product and date replaces the previous saved prediction for that combination.

Account registration and authentication use `users.csv` through the application's authentication utilities. The login interface supports creating the first account and subsequently signing in. The bakery profile page also allows users to view and update product prices. However, the bakery name, location, contact number, and coordinates displayed on that page are currently interface-level fields and are not persisted when the page is left.

### 4. Weather, Calendar Features, and Demand Forecasting

The forecasting pipeline combines product information with date-specific features and weather information before passing the inputs to the trained XGBoost regression model.

Weather data is handled according to the purpose of the operation:

- **Historical initialization:** The Open-Meteo historical weather API supplies weather data used to enrich the original sales records.
- **Daily entries:** The application retrieves weather information for the recorded day and stores it alongside the production and sales data.
- **Demand forecasting:** The Open-Meteo forecast API supplies expected weather conditions for the forecast date.

The `backend/weather.py` module handles these API requests and converts weather codes into readable conditions. The `backend/holidays.py` module uses the `holidays` library to determine public holidays and the dates immediately before and after them.

For each product, the forecasting module constructs the input features expected by the trained model. These include:

- Product identity and applicable base price.
- Day of the week, month, season, and weekend status.
- Temperature, rainfall, and weather condition.
- Public-holiday indicators and indicators for the days before and after a holiday.

The `ml/predict.py` module arranges these features in the required order and passes them to the saved model in `models/demand_model.pkl`. The model produces a demand estimate, which is rounded to a whole number and constrained to be non-negative.

The forecasting page presents predictions for the products in the bakery's product list, along with a total predicted demand and the relevant weather and holiday information. These predictions are estimates intended to support the operator's production decisions, rather than automatically determining production quantities.

### 5. Model Training, Evaluation, and Updating

The model training process is implemented in `ml/train.py` and can be initiated through the Model Management page.

The training pipeline reads the current `bakery_data.csv` dataset, sorts the records chronologically, and separates the earlier dates for training from the later dates for testing. It uses `Units_Sold` as the target and the same twelve product, price, weather, and calendar features used by the prediction pipeline.

Categorical features are transformed using one-hot encoding, while numerical features are passed through. The training pipeline then tunes an XGBoost regressor and evaluates the candidate model using metrics including mean absolute error (MAE) and root mean squared error (RMSE), with weighted absolute percentage error (WAPE) also reported when available.

The candidate model is compared with the currently saved model. The existing model is retained unless the candidate performs better according to the implemented evaluation process. If the candidate is accepted and saved, the prediction module reloads the updated model so subsequent forecasts can use it.

Recording daily entries and retraining the model are separate operations. Adding entries updates the operational dataset; retraining subsequently uses the accumulated dataset to build and evaluate a candidate model. This allows newly collected bakery records to contribute to future forecasts when training completes successfully and the candidate meets the replacement criteria.

## Technology Stack

Bakery Demand AI combines machine learning, data processing, external APIs, and an interactive web interface to support bakery demand forecasting.

| Technology | Role in the Project |
|---|---|
| **Python** | Main programming language used to implement the application, data processing, and machine learning pipeline. |
| **Streamlit** | Provides the interactive web interface for demand forecasting, daily production and sales entries, account access, bakery profile management, and model retraining. |
| **Pandas** | Handles data loading, transformation, validation, and management of the bakery's CSV datasets. |
| **NumPy** | Supports numerical operations within the machine learning workflow. |
| **Scikit-learn** | Provides data preprocessing, one-hot encoding, chronological train-test splitting, hyperparameter tuning utilities, and model evaluation metrics. |
| **XGBoost** | Implements the regression model used to predict demand for individual bakery products. |
| **Joblib** | Saves and loads the trained demand prediction model. |
| **Open-Meteo API** | Supplies historical weather data for dataset initialization and forecast weather data for demand prediction. |
| **Python `holidays` library** | Identifies Sri Lankan public holidays and provides holiday-related calendar information. |
| **Requests** | Sends HTTP requests to the Open-Meteo API to retrieve weather data. |
| **CSV files** | Provide storage for historical sales, operational records, forecast history, product price history, and account information. |
| **Jupyter Notebooks** | Support data analysis and model development through exploratory analysis and experimentation. |

## Project Structure

The repository separates the user interface, backend operations, machine learning pipeline, data storage, and initialization scripts.

```text
Bakery-Demand-AI/
├── app.py
├── config.py
├── backend/
│   ├── data.py
│   ├── forecast.py
│   ├── holidays.py
│   └── weather.py
├── data/
│   ├── bakery_data.csv
│   ├── forecast_history.csv
│   ├── kandy_bakery_sales_2024_2025.csv
│   ├── price_history.csv
│   └── users.csv
├── ml/
│   ├── predict.py
│   └── train.py
├── models/
│   └── demand_model.pkl
├── notebooks/
│   ├── 01_data_analysis.ipynb
│   └── 02_model_development.ipynb
├── pages/
│   ├── daily_entries.py
│   ├── forecast.py
│   ├── login.py
│   ├── profile.py
│   └── training.py
├── setup/
│   └── initialize_data.py
├── utils/
│   ├── auth.py
│   └── ui.py
├── .streamlit/
│   └── config.toml
├── .gitignore
├── requirements.txt
└── README.md
```

### Key Directories and Files

- **`app.py`** — Entry point for the Streamlit application and starting point for user navigation.
- **`pages/`** — Contains the individual interfaces for recording daily production and sales, viewing demand forecasts, signing in, managing the bakery profile, and retraining the model.
- **`backend/`** — Handles bakery data operations, forecast generation, weather retrieval, and public-holiday processing.
- **`ml/`** — Contains the training and prediction pipelines, including model preprocessing, evaluation, and loading.
- **`models/`** — Stores the trained XGBoost model used to generate demand predictions.
- **`data/`** — Contains the original historical sales dataset and the CSV files used for operational records, saved forecasts, product price history, and account information.
- **`notebooks/`** — Contains the notebooks used for data analysis and model development.
- **`setup/`** — Contains the initialization script that enriches the original historical sales data and creates the initial operational dataset.
- **`utils/`** — Provides shared authentication and user-interface utilities.
- **`config.py`** — Stores the fixed bakery configuration, including its geographical coordinates for weather requests.
- **`.streamlit/config.toml`** — Contains the Streamlit application configuration.
- **`requirements.txt`** — Lists the Python dependencies required to install and run the application.
- **`.gitignore`** — Specifies files and directories that should be excluded from version control.

## Setup and Installation

### Prerequisites

Before running Bakery Demand AI, ensure that you have:

- Python installed.
- Git installed to clone the repository.
- An internet connection for retrieving weather data from the Open-Meteo API.

### 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/thavinsa17/Bakery-Demand-AI.git
cd Bakery-Demand-AI
```

### 2. Create and Activate a Virtual Environment

Create an isolated Python environment for the project:

```bash
python -m venv .venv
```

Activate it using the appropriate command for your operating system.

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Initialize the Dataset

If `data/bakery_data.csv` has not yet been created, initialize it from the original historical sales dataset:

```bash
python setup/initialize_data.py
```

Run this initialization step only once when creating the initial dataset. The script generates the enriched operational dataset using the original sales records, historical weather information, and calendar features. It does not modify the original historical CSV.

Do not rerun initialization on an existing operational dataset unless you intentionally want to recreate it.

### 5. Launch the Application

Start the Streamlit application from the project root:

```bash
streamlit run app.py
```

Streamlit will provide a local URL that you can open in your web browser to access Bakery Demand AI.

### 6. Sign In

Open the application and use the login page to create the first account, if no account has been registered, or sign in with the existing credentials. After signing in, use the sidebar to navigate between the available application pages.

### Notes

- The application uses Open-Meteo to retrieve weather information, so weather-dependent features require an internet connection.
- The original historical sales dataset must be available in the `data/` directory when initializing the operational dataset.
- Keep the original historical CSV unchanged. Daily records are stored in `data/bakery_data.csv`.
- Model retraining is available through the Model Management page and is separate from recording daily entries.

## Feature Implementation Status

### Functional Features

- **Demand forecasting:** Generates next-day demand predictions for individual bakery products using a trained XGBoost regression model, product prices, weather information, and calendar features.
- **Daily production and sales recording:** Allows users to record the quantities of products produced and sold. The application validates entries, prevents duplicate records for the same product and date, and calculates leftover quantities.
- **Weather and holiday integration:** Retrieves historical and forecast weather information through the Open-Meteo API and identifies Sri Lankan public holidays using the Python `holidays` library.
- **Product price management:** Records product price changes with effective dates, preserves previous price records, and selects the applicable price for a forecast date.
- **Forecast history:** Stores demand predictions by product and date, allowing saved forecasts to be retrieved. A new prediction for the same product and date replaces the previously stored prediction.
- **Model retraining and evaluation:** Allows the operator to manually initiate model retraining through the Model Management page. The training process uses the available operational dataset to train and evaluate a candidate XGBoost model. The existing model is retained unless the candidate performs better according to the implemented evaluation process. Manual retraining is intentional, allowing the operator to decide when the model should be updated rather than triggering retraining whenever a new record is entered.
- **Account registration and sign-in:** Supports initial account registration and subsequent sign-in using CSV-based account storage.

### Partially Implemented Features and Limitations

- **Bakery profile management:** The profile page displays bakery information, including the bakery name, location, contact number, and coordinates. However, changes to these fields are not persisted. Product price updates are supported separately through the price-history functionality.
- **Account management:** The current implementation supports registering the first account and signing in. It does not provide a complete multi-user management system.
- **Data storage:** The application uses CSV files for operational records, forecast history, product prices, and account information. This provides persistent storage for the prototype, but the application does not use a database management system.
- **Synthetic historical dataset:** The original `kandy_bakery_sales_2024_2025.csv` dataset was generated using ChatGPT and contains entirely synthetic production and sales data. Historical weather and calendar features are incorporated during initialization, but the underlying production and sales records do not represent verified transactions from a real bakery. Consequently, the project demonstrates a demand-forecasting workflow rather than establishing reliable real-world forecasting performance. Evaluating practical accuracy would require actual historical sales data and validation against real bakery operations.

### Mocked Features

No additional features are explicitly classified as mocked in the current implementation. The limitations described above concern incomplete functionality, implementation choices, or the use of synthetic data rather than features that are explicitly simulated in place of real functionality.

## Demo and Deliverables

### Project Demonstration

The project demonstration showcases the main features of Bakery Demand AI, including demand forecasting, daily production and sales recording, product price management, and model retraining and evaluation.

### Project Resources

- **Source Code:** [Bakery Demand AI — GitHub Repository](https://github.com/thavinsa17/Bakery-Demand-AI)
- **Demonstration Video:** *Add demonstration video link.*
- **Business Case Document:** *Add document link.*
- **Presentation Slides:** *Add presentation link.*
- **AI Usage Report:** *Add report link.*

Team 

Bakery Demand AI was developed by:

[Team Member 1] — [Role or contribution]

[Team Member 2] — [Role or contribution]

[Team Member 3] — [Role or contribution]