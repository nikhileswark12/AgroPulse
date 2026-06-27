# AgroPulse

![CI](https://github.com/nikhileswark12/AgroPulse/actions/workflows/ci.yml/badge.svg)

AgroPulse is an open-source Flask application that provides market insights, price forecasting, and recommendation utilities for Indian agricultural commodity markets (mandis). The app combines historical mandi price data, lightweight ML models, and an interactive dashboard to help farmers, traders, and analysts explore price trends and generate short-term forecasts.

Key goals:
- Make mandi price data and model predictions accessible via a clean web UI and a small REST API.
- Enable reproducible model training and lightweight inference for quick local experiments.
- Provide clear developer workflows for extending models and data ingestion.

Features
--------
- Interactive dashboard with historical price charts and comparison views.
- Prediction endpoint and visualization for short-term price forecasts.
- Recommendation utilities for basic market insights.
- Simple ML training scripts and a reproducible data layout under `ml/`.

Tech stack
----------
- Python 3.10+ (tested on 3.10–3.11)
- Flask for the web server and routing
- MongoDB for lightweight data storage
- Pandas / scikit-learn (or lightweight alternatives) for model training

Quick start (development)
-------------------------
Prerequisites:
- Python 3.10 or newer
- MongoDB (local or hosted)
- Git

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with these minimum values:

```env
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://localhost:27017/agropulse
FLASK_ENV=development
```

4. Ensure the sample dataset exists:

- `ml/data/mandi_prices.csv` (a small sample is included in the repo)

5. Run the app locally:

```powershell
python app.py
```

Then open http://localhost:5000 in your browser.

Configuration
-------------
- Environment variables are read from `.env` (see `config.py` for keys used).
- `MONGO_URI` points to your MongoDB server/database.
- `SECRET_KEY` is used by Flask for session signing.

Project structure (important files)
----------------------------------
- `app.py` — application entrypoint and blueprint registration
- `config.py` — configuration loader (env / defaults)
- `routes/` — Flask blueprints that serve pages and API endpoints
   - `prediction_routes.py`, `price_routes.py`, `market_routes.py`, `auth_routes.py`
- `services/` — business logic (prediction, price lookup, recommendations)
- `ml/` — ML helper scripts
   - `train_model.py` — training pipeline
   - `predict.py` — model inference
   - `feature_engineering.py` — feature transforms
- `models/` — packaged model loaders / helper wrappers
- `utils/` — DB connection, helpers, and validators

Dataset & ML
------------
- The project includes a small CSV of mandi prices at `ml/data/mandi_prices.csv`.
- To retrain models locally:

```powershell
python ml/train_model.py --data ml/data/mandi_prices.csv --out models/latest_model.pkl
```

- To run a single prediction from the CLI:

```powershell
python ml/predict.py --model models/latest_model.pkl --input '{"district":"xyz","commodity":"wheat","days":7}'
```

API reference (selected endpoints)
---------------------------------
> **Note**: For backward compatibility, legacy `/api/*` endpoints remain supported and will return a `308 Permanent Redirect` to their corresponding `/api/v1/*` endpoints.

- `GET /` — Home page (dashboard)
- `GET /prediction` — Prediction UI page
- `POST /api/v1/predict` — Run a prediction (JSON body, returns forecast)
- `GET /api/v1/predict/history` — Retrieve stored prediction history

Example: POST a prediction request (JSON)

```http
POST /api/v1/predict HTTP/1.1
Content-Type: application/json

{
   "district": "Indore",
   "commodity": "Wheat",
   "horizon": 7
}
```

Response (example):

```json
{
   "commodity": "Wheat",
   "district": "Indore",
   "horizon": 7,
   "predictions": [ ... ],
   "meta": { "model_version": "v1", "generated_at": "2026-06-14T12:00:00Z" }
}
```

Development notes
-----------------
- Database: sample data uses MongoDB; use `utils/db_connection.py` to inspect connection handling.
- Frontend: templates are in `templates/` and static assets in `static/`.
- Tests: no automated test suite included; consider adding unit tests for `services/` and `ml/` scripts.

Contribution
------------
- Fork the repository, create a feature branch, and open a PR with a clear description.
- Keep changes focused and add unit tests where appropriate.

Troubleshooting
---------------
- If the app cannot connect to MongoDB, verify `MONGO_URI` and that MongoDB is running.
- If model inference fails, ensure `models/latest_model.pkl` exists and the model version matches code expectations.

Next steps
----------
- Add unit tests for core services and ML helpers.
- Add a small Dockerfile / docker-compose for local development if desired.

License
-------
This project is provided under the terms of the MIT license. See the `LICENSE` file for details.

Contact
-------
If you need help, open an issue or contact the maintainers via the repository.

