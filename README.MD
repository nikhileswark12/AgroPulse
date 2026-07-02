# AgroPulse

![CI](https://github.com/nikhileswark12/AgroPulse/actions/workflows/ci.yml/badge.svg)

## Intelligent Agricultural Market Intelligence & Price Forecasting Platform

AgroPulse is an intelligent agricultural market intelligence platform designed to empower farmers, traders, researchers, and agricultural organizations with data-driven insights into commodity markets. By combining historical mandi price data, predictive machine learning, and interactive visualization, the platform enables users to analyze market trends, compare prices across regions, and generate reliable short-term forecasts that support informed agricultural decision-making.

Agricultural commodity prices are influenced by numerous dynamic factors, including seasonal production, weather conditions, regional demand, transportation costs, government policies, and market volatility. Access to accurate and timely market intelligence remains a significant challenge, often forcing stakeholders to rely on fragmented information and manual analysis before making critical decisions. AgroPulse addresses this challenge by providing a unified platform that transforms raw agricultural market data into meaningful insights through modern web technologies and predictive analytics.

Designed with scalability and maintainability in mind, AgroPulse combines a modular Flask backend, machine learning pipelines, and an interactive web interface to create a comprehensive agricultural analytics ecosystem. The platform serves both end users seeking actionable market intelligence and developers interested in extending its data ingestion, forecasting, and analytical capabilities.

---

## Vision

To build a scalable and intelligent agricultural market intelligence platform that enables proactive, data-driven decision-making through predictive analytics, machine learning, and real-time commodity market insights.

---

## Problem Statement

Agriculture remains one of the most important sectors of the economy, yet access to reliable market intelligence continues to be limited for many stakeholders. Commodity prices fluctuate daily due to changes in supply, demand, transportation, climate, and regional economic conditions. While large volumes of market data are published through government agencies and agricultural organizations, this information is often fragmented, difficult to interpret, and inaccessible to users without technical expertise.

As a result, farmers frequently make selling decisions without understanding historical pricing trends or expected market movements, while traders and analysts spend significant time collecting and comparing information from multiple sources before making purchasing decisions.

Some of the primary challenges include:

* Limited accessibility to organized mandi price information.
* Difficulty analyzing historical commodity price trends.
* Absence of reliable short-term price forecasting tools.
* Manual comparison of prices across multiple agricultural markets.
* Lack of centralized analytical platforms for agricultural intelligence.
* Limited adoption of machine learning for agricultural decision support.

AgroPulse addresses these challenges by integrating historical market analysis, predictive machine learning models, visualization tools, and intelligent recommendation capabilities into a unified platform that simplifies agricultural market analysis and supports informed decision-making.

---

## Core Features

AgroPulse provides a comprehensive collection of tools for agricultural market analysis and predictive intelligence, including:

* Interactive dashboard for exploring historical commodity price trends.
* AI-powered commodity price forecasting using machine learning models.
* Seven-day price prediction with confidence intervals.
* Historical market analytics through interactive charts and visualizations.
* Commodity price comparison across multiple regional mandis.
* User authentication with email verification and password recovery.
* Administrative tools for automated dataset ingestion and market data updates.
* RESTful API for accessing market information and prediction services.
* Reproducible machine learning training and inference workflows.
* Modular architecture designed for scalability and future enhancements.

---

## Technology Stack

### Backend

* Python 3.11
* Flask
* Gunicorn
* Flask-Limiter
* Flask-Mail
* bcrypt
* itsdangerous

### Machine Learning

* Scikit-learn
* Pandas
* NumPy

### Database

* MongoDB
* Redis (Optional)

### Frontend

* HTML5
* Jinja2 Templates
* Vanilla JavaScript
* Bootstrap
* Chart.js
* CSS

---

## System Architecture

AgroPulse follows a modular, service-oriented architecture that separates presentation, business logic, data processing, and machine learning into independent layers.

The frontend delivers an interactive user experience for exploring agricultural market data through dynamic dashboards, comparison tools, and prediction interfaces. Requests are processed by a Flask backend responsible for authentication, business logic, REST API endpoints, and administrative operations.

Historical market information is stored within MongoDB, while Redis can optionally provide caching and rate-limiting support. Machine learning functionality is implemented through an independent prediction pipeline, allowing models to be retrained as new market data becomes available without affecting the primary application.

The platform is designed around modular components that simplify maintenance, encourage extensibility, and support deployment across local development environments as well as cloud infrastructure.

---

## Design Principles

AgroPulse is developed around several key architectural principles:

* Modular application architecture.
* Clean separation between business logic and presentation.
* Reproducible machine learning workflows.
* Secure authentication and user management.
* Scalable and maintainable backend services.
* Lightweight deployment with minimal infrastructure requirements.
* Extensible architecture for future agricultural intelligence capabilities.
* Reliable and transparent data-driven decision support.

---

## Future Scope

AgroPulse is designed as a continuously evolving agricultural intelligence platform. Future enhancements include integration with live government market APIs, weather-aware forecasting models, deep learning-based price prediction, geospatial visualization of mandi locations, multilingual support for regional users, personalized crop recommendations, mobile applications, advanced reporting dashboards, and intelligent recommendation systems for crop planning and market optimization.

The long-term objective is to transform AgroPulse into a comprehensive agricultural decision-support ecosystem that combines historical market intelligence, predictive analytics, and real-time data integration to improve efficiency, profitability, and sustainability across the agricultural supply chain.

---

## Quick Start (Local Development)

### Prerequisites

* Python 3.10 or newer
* MongoDB (Local Instance or MongoDB Atlas)
* Docker & Docker Compose (Optional)
* Git
### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/nikhileswark12/AgroPulse.git
cd AgroPulse
```

#### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
```

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

---

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

#### 4. Configure Environment Variables

Create a `.env` file in the project root and configure the required application settings.

```env
FLASK_ENV=development

SECRET_KEY=your-secret-key

MONGO_URI=mongodb://localhost:27017/

DATABASE_NAME=agropulse

ADMIN_KEY=your-admin-key

DATA_GOV_API_KEY=optional_api_key
```

Generate secure values for `SECRET_KEY` and `ADMIN_KEY` before running the application in production.

---

#### 5. Initialize the Database and Machine Learning Pipeline

Before starting the application, initialize the database, prepare the dataset, and train the prediction model.

```bash
python scripts/create_indexes.py

python scripts/populate_db.py

python ml/data_pipeline.py

python ml/train_model.py
```

---

#### 6. Run the Application

```bash
python app.py
```

The application will be available at:

```
http://localhost:5000
```

---

# Docker Deployment

AgroPulse can also be deployed using Docker Compose, allowing the entire application stack—including Flask, MongoDB, and Redis—to run in isolated containers.

### Initial Setup

```bash
make setup
```

### Build the Containers

```bash
make build
```

### Start the Application Stack

```bash
make up
```

### Verify Container Health

```bash
make health
```

### Stop the Containers

```bash
make down
```

Containerized deployment provides a reproducible development environment and closely mirrors production infrastructure.

---

# Testing

AgroPulse includes a comprehensive automated test suite covering authentication, prediction services, API endpoints, and application health checks.

Execute the complete test suite using:

```bash
FLASK_ENV=testing pytest tests/ -v
```

Running automated tests before deployment helps ensure application stability and prevents regressions as new features are introduced.

---

# Dataset & Machine Learning Pipeline

The prediction engine relies on historical agricultural market data for model training and inference.

### Updating the Dataset

1. Download the latest commodity price dataset from **AGMARKNET**.

2. Update the local dataset.

```bash
make update-data PATH=path/to/new_dataset.csv
```

3. Retrain the prediction model.

```bash
make retrain
```

4. Rebuild and restart the application.

```bash
make build
make up
```

---

### Training the Prediction Model

Models can also be trained directly from the command line.

```bash
python ml/train_model.py --data ml/data/mandi_prices.csv
```

---

### Running Predictions

Generate predictions using the command-line inference utility.

```bash
python ml/predict.py --input '{"crop":"Wheat","location":"Indore","state":"Madhya Pradesh","quantity":100}'
```

The prediction pipeline has been designed to be reproducible, allowing models to be retrained whenever new agricultural market data becomes available.

---

# Production Deployment

AgroPulse is deployment-ready and can be hosted on cloud platforms such as Render.

### Deployment Workflow

1. Push the repository to GitHub.
2. Create a new Render Web Service.
3. Connect the GitHub repository.
4. Render automatically detects the application configuration through `render.yaml`.
5. Configure the required environment variables.
6. Deploy the application.
7. Verify deployment through the health endpoint.

---

### Required Environment Variables

```text
SECRET_KEY
MONGO_URI
DATABASE_NAME
BASE_URL
CORS_ORIGINS
ADMIN_KEY
MAIL_SERVER
MAIL_PORT
MAIL_USERNAME
MAIL_PASSWORD
MAIL_DEFAULT_SENDER
REDIS_URL (Optional)
```

---

### MongoDB Atlas

For production deployments, MongoDB Atlas is recommended.

Basic setup involves:

* Creating a MongoDB Atlas cluster.
* Creating a database user.
* Configuring network access.
* Obtaining the MongoDB connection string.
* Assigning the connection string to `MONGO_URI`.

---

# Project Structure

```
AgroPulse/
│
├── ml/
│   ├── data/
│   ├── models/
│   ├── train_model.py
│   ├── predict.py
│   └── data_pipeline.py
│
├── routes/
│
├── services/
│
├── scripts/
│
├── templates/
│
├── static/
│
├── tests/
│
├── utils/
│
├── app.py
├── config.py
├── requirements.txt
├── requirements-dev.txt
└── render.yaml
```

The project follows a modular structure that separates routing, business logic, machine learning, utility functions, and presentation components, making the application easier to maintain and extend.

---

# Troubleshooting

### MongoDB Connection Issues

* Verify that MongoDB is running locally.
* Confirm that `MONGO_URI` is correctly configured.
* For MongoDB Atlas, ensure that network access rules permit incoming connections.

---

### Machine Learning Model Errors

If prediction requests fail, retrain the model.

```bash
python ml/train_model.py
```

This regenerates the serialized model files required for inference.

---

### Docker Issues

If containers fail to start, rebuild the application images.

```bash
make build
make up
```

Also verify that Docker Engine and Docker Compose are installed and running correctly.

---

# License

This project is licensed under the MIT License. See the `LICENSE` file for additional information.
