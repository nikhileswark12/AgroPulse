# AgroPulse

## Intelligent Agricultural Market Intelligence & Price Forecasting Platform

AgroPulse is an intelligent agricultural market intelligence platform that helps farmers, traders, researchers, and agricultural organizations make informed decisions through historical mandi price analysis, machine learning–based forecasting, and interactive visualizations.

---

## About the Project

AgroPulse centralizes agricultural market intelligence into a single platform by combining historical commodity price data, predictive analytics, and modern web technologies. It enables users to explore trends, compare prices across mandis, and generate short-term forecasts that support better agricultural decision-making.

## Key Features

- Historical mandi price analysis
- AI-powered price forecasting
- Seven-day commodity price prediction
- Interactive dashboards and visualizations
- Multi-mandi price comparison
- Authentication and user management
- REST API support
- Automated ML training pipeline
- Modular Flask architecture
- Deployment-ready with Docker and Render

## Tech Stack

| Category | Technologies |
|:---------|:-------------|
| **Languages** | <img src="https://skillicons.dev/icons?i=python,js,html,css" /> |
| **Frontend** | HTML5, Jinja2 Templates, Vanilla JavaScript, CSS, Bootstrap 5.3.2, Chart.js |
| **Backend** | <img src="https://skillicons.dev/icons?i=flask" /> Flask 3.0.0, Flask-CORS 4.0.0, Flask-Limiter 3.5.0, Flask-Mail, itsdangerous, Werkzeug, bcrypt, Gunicorn |
| **Database** | <img src="https://skillicons.dev/icons?i=mongodb,redis" /> MongoDB (PyMongo 4.6.0), Redis (Optional) |
| **Machine Learning** | Scikit-learn ≥ 1.4.0, Pandas ≥ 2.2.0, NumPy ≥ 1.26.0, Joblib ≥ 1.3.0 |
| **Tools** | <img src="https://skillicons.dev/icons?i=git,github,vscode,postman,docker" /> |

## System Architecture

```text
Frontend
    │
Flask Backend
    │
├── Authentication
├── REST APIs
├── Business Logic
├── ML Pipeline
│
MongoDB / Redis
```

## Project Structure

```text
AgroPulse/
├── ml/
├── routes/
├── services/
├── scripts/
├── static/
├── templates/
├── tests/
├── utils/
├── app.py
├── config.py
└── render.yaml
```

## Quick Start

```bash
git clone https://github.com/nikhileswark12/AgroPulse.git
cd AgroPulse

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -r requirements-dev.txt

python scripts/create_indexes.py
python scripts/populate_db.py
python ml/data_pipeline.py
python ml/train_model.py

python app.py
```

Application runs at:

```text
http://localhost:5000
```

## Environment Variables

```env
SECRET_KEY=
MONGO_URI=
DATABASE_NAME=
ADMIN_KEY=
DATA_GOV_API_KEY=
```

## Docker

```bash
make setup
make build
make up
make health
make down
```

## Machine Learning Pipeline

```bash
python ml/train_model.py
python ml/predict.py --input '{"crop":"Wheat"}'
```

## Testing

```bash
FLASK_ENV=testing pytest tests/ -v
```

## Deployment

The application is deployment-ready and supports platforms such as Render using the included `render.yaml`.

## Roadmap

- Live AGMARKNET integration
- Weather-aware forecasting
- Deep learning models
- Mobile application
- Multilingual support
- Advanced analytics dashboard

## Contributing

Contributions, bug reports, and feature requests are welcome.

## License

Licensed under the MIT License.
