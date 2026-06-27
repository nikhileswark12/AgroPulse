# System Design Document - AgroPulse

## 1. System Architecture
AgroPulse is designed as a three-tier web application optimized for quick read lookups and model prediction responses.

- **Presentation Layer**: Jinja2-rendered HTML templates utilizing vanilla JavaScript, Chart.js for data visualization, and Bootstrap for layout responsiveness.
- **Application Layer**: Flask application hosting modular routing controllers (blueprints), middleware filters (Flask-Limiter, CORS, Flask-Mail), and a business logic service layer.
- **Database & Model Layer**: MongoDB collection abstractions managed through a Singleton pymongo connection driver.

## 2. Component Design & Interactions
```mermaid
sequenceDiagram
    actor Farmer as User Browser
    participant App as Flask Router
    participant Serv as Prediction Service
    participant Cache as MongoDB predictions
    participant ML as ML Model Predictor

    Farmer->>App: POST /api/v1/predict (State, District, Crop)
    App->>Serv: get_prediction()
    Serv->>Cache: get_recent_prediction() (sliding 2 hr window)
    
    alt Cache Hit
        Cache-->>Serv: Return cached forecast
        Serv-->>App: Serialized response
    else Cache Miss
        Serv->>ML: predict_price()
        ML-->>Serv: Generate 7-day forecast & bounds
        Serv->>Cache: save_prediction()
        Serv-->>App: Serialized response
    end
    
    App-->>Farmer: Render forecast Chart & Advice
```

## 3. Machine Learning Model Architecture
- **Algorithm**: Random Forest Regressor (300 estimators, max depth 12).
- **Features**: Label-encoded values for `state`, `district`, and `crop` columns.
- **Inference Forecast Method**: Generates a 7-day trend based on seasonal coefficients (Rabi, Kharif, Zaid) added to the model's base crop valuation.
- **Confidence Intervals**: Computed dynamically by applying a scaling margin to the model's Mean Absolute Error (MAE).

## 4. Cache Policy
- Cached prediction items expire after **2 hours**.
- Stored fields: `crop`, `location`, `predicted_prices`, `trend`, `optimal_day`, `confidence`, `current_price`, and `created_at`.
