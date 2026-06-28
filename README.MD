# AgroPulse

![CI](https://github.com/nikhileswark12/AgroPulse/actions/workflows/ci.yml/badge.svg)

AgroPulse is an open-source Flask application that provides market insights, price forecasting, and recommendation utilities for Indian agricultural commodity markets (mandis). The app combines historical mandi price data, lightweight ML models, and an interactive dashboard to help farmers, traders, and analysts explore price trends and generate short-term forecasts.

Key goals:
- Make mandi price data and model predictions accessible via a clean web UI and a structured REST API.
- Enable reproducible model training and lightweight inference for quick local experiments.
- Provide clear developer workflows for extending models and data ingestion.

---

## Features
- **Interactive Dashboard**: Client-side dashboard with historical price charts, comparison tables, and quick action recommendations.
- **AI-Assisted Price Prediction**: Generates 7-day crop price forecasts with upper and lower confidence intervals using a Random Forest regression model.
- **Price Comparison**: Compares live prices across regional mandis, with client-side sorting by price or distance.
- **User Authentication**: Secure session-based signup, login, email verification, and password reset flows.
- **Admin Ingestion Services**: Force-reload commodity datasets in-memory and update records from AGMARKNET CSV inputs or dynamic data.gov.in API keys.

---

## Tech Stack
- **Backend**: Python 3.11, Flask 3.0.0, Gunicorn, Flask-Limiter, Flask-Mail, bcrypt, itsdangerous
- **Database**: MongoDB 7.0 (via PyMongo 4.6.0) & optional Redis (for rate-limit caching)
- **Machine Learning**: scikit-learn >= 1.4.0, pandas >= 2.2.0, numpy >= 1.26.0
- **Frontend**: HTML5, Jinja2 Templates, Vanilla JavaScript, CSS, Chart.js, Bootstrap v5.3.2

---

## Quick Start (Local Development)

### Prerequisites:
- Python 3.10 or newer
- MongoDB (local instance or MongoDB Atlas)
- Docker & Docker Compose (optional, for containerized run)
- Git

### 1. Create and Activate Virtual Environment:
```bash
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Python Dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for testing tools
```

### 3. Setup Configuration:
Create a `.env` file in the project root:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=agropulse
ADMIN_KEY=your-admin-reload-key # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
DATA_GOV_API_KEY=optional_data_gov_key_here
```

### 4. Initialize Database and ML Model:
Make sure you build indexes and process/train models before starting:
```bash
# Run database index initializer
python scripts/create_indexes.py

# Ingest sample prices
python scripts/populate_db.py

# Clean and split raw data
python ml/data_pipeline.py

# Train the prediction model
python ml/train_model.py
```

### 5. Run the Application:
```bash
python app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Docker & Docker Compose Setup
Alternatively, spin up the entire application stack (Flask web app, MongoDB, and Redis) locally with Docker:

1. **Initialize Setup**:
   ```bash
   make setup
   ```
2. **Build and Start containers**:
   ```bash
   make build
   make up
   ```
3. **Verify running containers**:
   ```bash
   make health
   ```
4. **Shutdown container stack**:
   ```bash
   make down
   ```

---

## Running Automated Tests
The project features a comprehensive `pytest` test suite covering authentication, API health, predictions, and history collections:
```bash
# Run all tests locally
FLASK_ENV=testing pytest tests/ -v
```

---

## Dataset, Ingestion & ML Pipeline

### Updating Mandi Prices:
To refresh the local `ml/data/mandi_prices.csv` dataset:
1. Download a fresh CSV from [AGMARKNET](https://agmarknet.gov.in) manually.
2. Run the update script specifying the CSV path:
   ```bash
   make update-data PATH=path/to/new_data.csv
   ```
3. Retrain the model on the updated data:
   ```bash
   make retrain
   ```
4. Rebuild/restart containers to apply the fresh model:
   ```bash
   make build && make up
   ```

### Command Line Model Operations:
- **Model Training**:
  ```bash
  python ml/train_model.py --data ml/data/mandi_prices.csv
  ```
- **CLI-Based Model Inference**:
  ```bash
  python ml/predict.py --input '{"crop":"Wheat","location":"Indore","state":"Madhya Pradesh","quantity":100}'
  ```

---

## Production Deployment Guide

### Deploying to Render.com:
1. Push your repository to GitHub.
2. Log in to [Render](https://render.com) and click **New > Web Service**.
3. Link your GitHub repository.
4. Render automatically applies configurations defined in [render.yaml](file:///f:/GitHub/AgroPulse/render.yaml).
5. Set these required configuration environment variables manually in the Render dashboard:
   - `MONGO_URI`: MongoDB Atlas production connection string.
   - `CORS_ORIGINS`: `https://your-app-name.onrender.com`
   - `BASE_URL`: `https://your-app-name.onrender.com`
   - `ADMIN_KEY`: A secure generated token to run administrative endpoints.
   - `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` (SMTP server details).
   - `REDIS_URL` (optional, leave blank to default to in-memory rate limiting).
6. Click **Deploy**.
7. Confirm deployment by sending a request to the health checker endpoint: `https://your-app-name.onrender.com/health`.

### MongoDB Atlas Setup (Production):
1. Sign up on [MongoDB Atlas](https://cloud.mongodb.com).
2. Create a free M0 tier cluster database.
3. Add a database user with read/write permissions.
4. Set IP Access Whitelist to `0.0.0.0/0` (Render uses dynamic IP blocks).
5. Extract your connection string and supply it as `MONGO_URI` in the Render environment variables.

---

## Project Structure
- [app.py](file:///f:/GitHub/AgroPulse/app.py) — Application factory initialization and UI rendering routes.
- [config.py](file:///f:/GitHub/AgroPulse/config.py) — Configuration presets for development, testing, and production.
- `routes/` — Flask blueprints serving JSON REST API endpoints under `/api/v1/`.
  - [auth_routes.py](file:///f:/GitHub/AgroPulse/routes/auth_routes.py) — Auth operations (session, reset token flows).
  - [admin_routes.py](file:///f:/GitHub/AgroPulse/routes/admin_routes.py) — In-memory reloading services, validated by `X-Admin-Key` headers.
  - [prediction_routes.py](file:///f:/GitHub/AgroPulse/routes/prediction_routes.py) — Inference and predictions log routing.
  - [price_routes.py](file:///f:/GitHub/AgroPulse/routes/price_routes.py) — Market price analytics.
- `services/` — Business logic implementations (ML predictions, calculations, recommendation strategies).
- `ml/` — Machine learning scripts and pipelines.
- `utils/` — Common helpers, DB singleton connector, validations.

---

## Pre-deployment Checklist
- [ ] Running `make test` or `pytest tests/` succeeds locally.
- [ ] Health check response returns `model_loaded: true` locally.
- [ ] `MONGO_URI` is mapped to MongoDB Atlas production instance.
- [ ] `SECRET_KEY` is configured to a secure, random value.
- [ ] `CORS_ORIGINS` and `BASE_URL` exactly match the production deployment address.

---

## Troubleshooting
- **MongoDB Connection Error**: Check your connection credentials and verify the MongoDB server is up. On Atlas, ensure `0.0.0.0/0` is whitelisted.
- **Model Inference Failures**: Ensure model pickle files have been trained/generated (run `python ml/train_model.py` to regenerate pickles).

---

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.
