# AgroPulse

AgroPulse is a Flask-based agricultural market prediction dashboard. It provides price and mandi analytics, prediction results, and user-facing pages powered by a MongoDB backend.

## Project structure

- `app.py` - Flask application entrypoint.
- `routes/` - API and frontend routes.
- `services/` - Business logic for predictions, pricing, and recommendations.
- `ml/` - Machine learning helper scripts and dataset.
- `templates/` - HTML templates.
- `static/` - CSS and JavaScript assets.
- `utils/` - shared helpers and database connection logic.

## Prerequisites

- Python 3.14
- MongoDB running locally or remotely
- Git

## Setup

1. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with at least these values:

   ```env
   SECRET_KEY=replace-with-your-secret
   MONGO_URI=mongodb://localhost:27017/
   ```

4. Keep the dataset in place:

   - `ml/data/mandi_prices.csv`

## Run the app

```powershell
python app.py
```

Open `http://localhost:5000` in your browser.

## Notes

- The repository ignores generated Python caches, logs, and ML model artifacts.
- If you need to retrain models, use the scripts in `ml/`.
- `app.py` initializes MongoDB and registers API blueprints.

## Git ignore behavior

The `.gitignore` file is configured to keep source code committed while excluding:

- Python caches: `__pycache__/`, `*.pyc`
- log files: `logs/`
- environment files: `.env`
- generated ML artifacts: `ml/*.pkl`, `ml/*.png`, and `ml/ml/`

## Project pages

- `/` - home
- `/login` - login page
- `/dashboard` - dashboard
- `/prediction` - prediction page
- `/comparison` - comparison page
- `/about` - about page

## API endpoints

- `POST /api/predict` - prediction endpoint
- `GET /api/predict/history` - prediction history

---

If you want, I can also add a small script to rebuild the ignored ML artifacts.
