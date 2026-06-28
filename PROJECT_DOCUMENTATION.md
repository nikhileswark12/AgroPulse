# AgroPulse - Complete Project Documentation

This documentation provides an exhaustive, source-mapped technical specification and blueprint of the AgroPulse repository. All details are extracted directly from the code files and scripts in the workspace.

---

## 1. Executive Summary

*   **Project Name**: AgroPulse
*   **Purpose**: AgroPulse is a market intelligence and predictive analysis platform tailored for Indian agricultural commodities. It aims to eliminate information asymmetry, bypass middleman exploitation, and help farmers make informed decisions about when and where to sell their crops.
*   **Main Features**:
    *   **Landing Page**: Interactive portal displaying problems (e.g., market transparency, middlemen) and public crop lookup options.
    *   **Farmer Dashboard**: Authenticated card-based overview tracking the user's primary crop, nearest mandi, best prices, and quick recommendations.
    *   **Price Comparison**: A dynamic list comparing prices across multiple regional mandis, with client-side sorting by price or distance.
    *   **AI-Assisted Price Prediction**: A 7-day crop price forecast with upper and lower confidence intervals, generated using a trained Random Forest regression model.
    *   **User Authentication**: Secure session-based signup, login, email verification, and password reset flows.
    *   **Prediction History**: A user-specific log of past price forecast queries.
    *   **Mandi Data Ingestion Service**: Script-based ingestion to clean, validate, and merge fresh commodity pricing records into the core CSV database.
    *   **Admin Reload capability**: Endpoint to reload the updated CSV dataset into memory without service disruption, secured by `X-Admin-Key` header verification.
    *   **Centralized Database Connector**: Singleton client manager to prevent duplicate connection sockets to MongoDB.
*   **Target Users**:
    *   **Farmers**: Seeking optimization of crop sale timing and mandi selection.
    *   **FPOs (Farmer Producer Organizations)**: Aggregators comparing prices across regions to optimize collective bargaining power.
    *   **Traders/Analysts**: Monitoring price trends and predicting commodity movements.
*   **Business Workflow**:
    ```text
    User -> Lands on Homepage -> Logs in / Registers (via email link)
          -> Accesses Dashboard -> Selects Crop, State, & District
          -> System runs ML Inference (falls back to CSV stats if model is absent)
          -> Renders 7-day Price Forecast (Chart.js) and recommendations (Sell/Wait)
          -> Saves query to history -> User reviews history or compares other mandis
    ```
*   **Technology Stack**:
    *   **Backend**: Flask 3.0.0, Flask-CORS 4.0.0, Flask-Limiter 3.5.0, Flask-Mail, itsdangerous, Werkzeug, bcrypt, gunicorn (documented in [requirements.txt](file:///f:/GitHub/AgroPulse/requirements.txt)).
    *   **Database**: MongoDB (via PyMongo 4.6.0) and Redis (optional, for rate-limiting storage).
    *   **Machine Learning**: scikit-learn >= 1.4.0, pandas >= 2.2.0, numpy >= 1.26.0, joblib >= 1.3.0.
    *   **Frontend**: HTML5, Jinja2 Templates, Vanilla JavaScript, CSS, Chart.js, Bootstrap (v5.3.2 CDN).

---

## 2. Repository Structure

### Complete Folder Tree
```text
AgroPulse/
├── .github/
│   └── workflows/
│       ├── ci.yml            # CI Pipeline (Runs pytest and sets up test MongoDB)
│       └── deploy-check.yml   # Pre-deploy Checks (Dockerfile build and env tests)
├── ml/                       # Machine Learning Code, Data & Model Pickles
│   ├── data/
│   │   ├── mandi_prices.csv      # Raw CSV Dataset (Primary Source of truth)
│   │   ├── processed_prices.csv  # Cleansed and engineered dataset
│   │   ├── train.csv             # Train split (70%)
│   │   ├── val.csv               # Validation split (15%)
│   │   └── test.csv              # Test split (15%)
│   ├── trained_model.pkl         # Trained Random Forest Regressor Pickle
│   ├── model_metadata.pkl        # Accuracy metrics (MAE, RMSE, R2) and mappings
│   ├── crop_encoder.pkl          # LabelEncoder for Crop column
│   ├── state_encoder.pkl         # LabelEncoder for State column
│   ├── district_encoder.pkl      # LabelEncoder for District column
│   ├── feature_cols.pkl          # List of active training feature keys
│   ├── data_pipeline.py          # Data cleansing and train/val/test splitting
│   ├── feature_engineering.py    # Temporal, lag, roll, and cyclical engineering
│   ├── predict.py                # Runtime Model Inference & Fallback logic
│   └── train_model.py            # Training pipeline with evaluation & cv
├── models/                   # Database Collection Entities (Denormalized)
│   ├── __init__.py
│   ├── market.py             # Markets Collection Access Methods
│   ├── predict.py            # Predictions Cache Collection Access Methods
│   └── price.py              # Prices Collection Access Methods
├── routes/                   # Flask Blueprint Route Managers (API prefixes /v1)
│   ├── __init__.py
│   ├── admin_routes.py       # Reload CSV dataset in-memory cache API
│   ├── auth_routes.py        # Login, Register, Verify, Reset APIs
│   ├── mandi_routes.py       # CSV-Backed comparison API
│   ├── market_routes.py      # MongoDB Market Queries API
│   ├── prediction_routes.py  # Prediction inference & history CRUD APIs
│   └── price_routes.py       # MongoDB Price statistics & current pricing APIs
├── scripts/                  # DB Ingestion, Update & Index Scripts
│   ├── create_indexes.py     # MongoDB unique, compound & single index creation
│   ├── populate_db.py        # Sample data populator for local testing
│   └── update_mandi_data.py  # Clean, validate, deduplicate, and ingest mandi CSV
├── static/                   # Shared CSS and JavaScript Assets
│   ├── css/
│   │   └── site.css          # Core Shared Layout and Element Styles
│   └── js/
│       ├── site.js           # Global Nav, Alert, and Button Spin helpers
│       ├── utils.js          # Fetch wrapper, 401 redirect, and error handles
│       └── prediction_metadata.js # Dynamic select-dropdown populator from API
├── templates/                # Server-rendered HTML Layout Pages
│   ├── index.html            # Landing / Marketing Page
│   ├── login.html            # User authentication form page
│   ├── forgot_password.html  # Forgot password email request page
│   ├── reset_password.html   # Password reset token completion page
│   ├── dashboard.html        # Farmer overview dashboard page
│   ├── prediction.html       # ML Interactive Prediction & Chart.js graph
│   ├── comparison.html       # Mandi list and price comparison page
│   ├── history.html          # Saved predictions listing and pager
│   └── about.html            # Core FAQ and Contact Form page
├── tests/                    # Automation testing suites
│   ├── conftest.py           # Pytest fixtures and mock DB configs
│   ├── test_auth.py          # Session authentication tests
│   ├── test_health.py        # Application status tests
│   ├── test_mandi.py         # price list and coordinate comparison tests
│   └── test_prediction.py    # Prediction cache, prediction history, and deletion tests
├── utils/                    # Application Utilities and Global Helpers
│   ├── __init__.py
│   ├── db_connection.py      # Singleton MongoDB connection wrapper
│   ├── helpers.py            # Date ranges, distance, formatters, and pagination
│   ├── logger.py             # Dual Stream/Rotating file log configuration
│   └── validators.py         # Form request payload input validations
├── app.py                    # Flask Application Factory and Page Routing
├── config.py                 # Configuration Map and Application Constraints
├── requirements.txt          # Python Dependency Declarations
├── requirements-dev.txt      # Development Tools dependencies
├── README.MD                 # High-Level Usage Overview and Deployment Guide
├── Dockerfile                # Gunicorn-backed Container Build Steps
├── docker-compose.yml        # Development Stack (Flask, MongoDB, Redis)
└── Makefile                  # Automation Scripts (run, test, retrain, db)
```

### Folder & File Purposes
*   **`.github/workflows/`**: Handles continuous integration pipeline (`ci.yml`) and deploy check script verification (`deploy-check.yml`).
*   **`ml/`**: Machine learning model files, including pipeline engineering scripts (`data_pipeline.py`, `feature_engineering.py`), training wrappers (`train_model.py`), runtimes (`predict.py`), encoders (`crop_encoder.pkl`), and datasets (`data/mandi_prices.csv`).
*   **`models/`**: Abstract classes referencing collections directly: `market.py` (`markets` collection), `price.py` (`prices` collection), and `predict.py` (`predictions` collection).
*   **`routes/`**: Group of Blueprint files handling Flask requests, routing variables, and responding with JSON collections.
*   **`scripts/`**: Populates test databases, sets collection indexes, and executes data merging.
*   **`static/`**: Client assets, including CSS overrides (`site.css`), request abstractions (`utils.js`), populating dropdowns (`prediction_metadata.js`), and helper scripts (`site.js`).
*   **`templates/`**: Server-rendered Jinja2 HTML layouts.
*   **`utils/`**: Shared functions including validation schemas (`validators.py`), connection singletons (`db_connection.py`), pagination and geographic math (`helpers.py`), and log formatters (`logger.py`).

### Architecture Overview
AgroPulse uses a layered architecture, splitting operations across specific boundaries:
```mermaid
flowchart TD
    Client[Browser UI] <-->|Fetch API calls| FlaskApp[Flask Application Factory app.py]
    FlaskApp <-->|URL Mapping & Limiting| Blueprints[Routes Layer routes/*]
    Blueprints <-->|Data Coercion & Validations| Validators[Validators Layer utils/validators.py]
    Blueprints <-->|Business Logic & Recommendations| Services[Services Layer services/*]
    Services <-->|Model Pickles / Inference| ML[ML Predictor ml/predict.py]
    ML <-->|Feature Construction| FE[Feature Engineer ml/feature_engineering.py]
    Services <-->|Query abstraction| Models[Models Layer models/*]
    Models <-->|Singleton MongoClient| DB[Database Handler utils/db_connection.py]
    DB <-->|Read / Write| MongoDB[(MongoDB Collections)]
```

### Dependency Map
*   [app.py](file:///f:/GitHub/AgroPulse/app.py) registers all blueprints from `routes/` under the `/api/v1` prefix and configures Flask-CORS, Flask-Limiter, Flask-Mail, logging, and global HTTP error pages.
*   [routes/auth_routes.py](file:///f:/GitHub/AgroPulse/routes/auth_routes.py) handles authentication, verifying passwords with `bcrypt` and sending timed reset tokens using `itsdangerous`. It uses the centralized connection in [utils/db_connection.py](file:///f:/GitHub/AgroPulse/utils/db_connection.py) to manage the `users` collection.
*   [routes/prediction_routes.py](file:///f:/GitHub/AgroPulse/routes/prediction_routes.py) imports [ml/predict.py](file:///f:/GitHub/AgroPulse/ml/predict.py) to run price prediction models, saving query records to the `prediction_history` collection.
*   [routes/price_routes.py](file:///f:/GitHub/AgroPulse/routes/price_routes.py) calls services from `services/` to fetch live prices and generate advice, utilizing validations from [utils/validators.py](file:///f:/GitHub/AgroPulse/utils/validators.py).
*   [routes/mandi_routes.py](file:///f:/GitHub/AgroPulse/routes/mandi_routes.py) reads directly from the dataset file `ml/data/mandi_prices.csv` to output compared prices.
*   [routes/admin_routes.py](file:///f:/GitHub/AgroPulse/routes/admin_routes.py) reloads the CSV dataset into the `current_app.mandi_data` cache.
*   [services/price_service.py](file:///f:/GitHub/AgroPulse/services/price_service.py) communicates with [models/price.py](file:///f:/GitHub/AgroPulse/models/price.py) and [models/market.py](file:///f:/GitHub/AgroPulse/models/market.py) to calculate price statistics and locate nearby mandis.
*   [services/prediction_service.py](file:///f:/GitHub/AgroPulse/services/prediction_service.py) coordinates calls to [ml/predict.py](file:///f:/GitHub/AgroPulse/ml/predict.py) and uses [models/predict.py](file:///f:/GitHub/AgroPulse/models/predict.py) to save and fetch cached predictions.
*   [services/recommendation_service.py](file:///f:/GitHub/AgroPulse/services/recommendation_service.py) accepts current pricing data and future forecasts to calculate potential profit gains and format wait/sell advice.
*   [models/market.py](file:///f:/GitHub/AgroPulse/models/market.py), [models/price.py](file:///f:/GitHub/AgroPulse/models/price.py), and [models/predict.py](file:///f:/GitHub/AgroPulse/models/predict.py) fetch their collections via `get_collection()` inside [utils/db_connection.py](file:///f:/GitHub/AgroPulse/utils/db_connection.py).

---

## 3. Frontend Analysis

### 3.1 Frontend Architecture
*   **Framework Used**: Server-rendered HTML templates utilizing Flask's Jinja2 engine. Responsive layouts are constructed via Bootstrap v5.3.2 components (in predictions page) and raw CSS flexbox in other templates.
*   **State Management**: Browser state is maintained through DOM values, session cookies, and client-side memory bindings (e.g., `window.PREDICTION_META` in [static/js/prediction_metadata.js](file:///f:/GitHub/AgroPulse/static/js/prediction_metadata.js)).
*   **Routing Structure**: Served via Flask routes in [app.py](file:///f:/GitHub/AgroPulse/app.py). Pages handle redirection by checking authorization check client-side using `window.checkAuth()` from [static/js/site.js](file:///f:/GitHub/AgroPulse/static/js/site.js).
*   **Component Hierarchy**:
    *   `Navbar`: Navigation header repeated on all pages.
    *   `Footer`: Copyright signature footer repeated on all pages.
    *   `Card Groups`: Card panels tracking dashboard metrics and prediction summaries.
    *   `Alert Box`: DOM element with id `#alertBox` displaying errors or success messages.
*   **Design Patterns**:
    *   Progressive enhancement of form controls.
    *   Asynchronous AJAX fetch commands through a global wrapper (`window.fetchJSON`).
    *   Cascading dropdown options where District options load dynamically based on the selected State.

### 3.2 Screens & Pages

| Page Name | Route | Purpose | User Actions | Components Used | Data Sources |
|---|---|---|---|---|---|
| **Landing** | `GET /` | Marketing & product entry | Lookup crop, navigate to signup or login | Navbar, Hero banner, search inputs, CTAs | Static templates, public metadata |
| **Login** | `GET /login` | User authentication | Submit email/password, navigate to forgot-password | Card, text inputs, error alert, submit spinner | `/api/v1/auth/login` |
| **Forgot Password** | `GET /forgot-password` | Request password reset | Enter email, submit request | Card, input, alert, login link | `/api/v1/auth/forgot-password` |
| **Reset Password** | `GET /password-reset/<token>` | Perform password reset | Enter and confirm new password, submit form | Card, inputs, alert, redirect timer | `/api/v1/auth/reset-password` |
| **Dashboard** | `GET /dashboard` | Authenticated overview | Navigate to predictions or comparison screens | Cards, welcome header, action buttons | Local placeholder info, `checkAuth()` |
| **Prediction** | `GET /prediction` | Dynamic crop forecasts | Select State, District, and Crop; click analyze | Dropdowns, Chart.js canvas, advice banner | `/api/v1/predict`, `/api/v1/predict/model-info` |
| **Comparison** | `GET /comparison` | Mandi prices lookup | Select crop, sort by price or distance | Dropdown, HTML tables, sort buttons | `/api/v1/mandi/compare?crop=crop_name` |
| **History** | `GET /history` | Historical logs | Paging navigation (previous/next) | Cards, list rows, pager buttons | `/api/v1/predict/history` |
| **About** | `GET /about` | FAQ & Contact Form | Submit feedback message, expand FAQ items | Accordion, contact form inputs, submit button | Static templates |

### 3.3 Wireframes

#### Landing/Home Page (`templates/index.html`)
```text
--------------------------------------------------------------------------------
Navbar: AgroPulse                                    Home | Compare | Login(Btn)
--------------------------------------------------------------------------------
Hero:
        🌾 AgroPulse - Fair Crop Prices for Farmers
        Empowering farmers with AI-driven commodity price intelligence.

        [ Select State (Select) ] [ Select District (Select) ] [ Analyze (Btn) ]
--------------------------------------------------------------------------------
Section: Problems We Solve
  [ Card: Lack of Info ]    [ Card: Unfair Middlemen ]    [ Card: No Forecasts ]
--------------------------------------------------------------------------------
Footer: © 2026 AgroPulse | Helping Farmers Earn Fair Prices
--------------------------------------------------------------------------------
```

#### Login Page (`templates/login.html`)
```text
--------------------------------------------------------------------------------
                                [ Centered Card ]
                                   AgroPulse
                             Login to your account

                             [ Alert Area (Hidden) ]

                             Email
                             [ Input: Email ]

                             Password
                             [ Input: Password ]

                             [ Login (Button) ]

                             Forgot Password?
                             Don't have an account? Sign up
                             ← Back to Home
--------------------------------------------------------------------------------
```

#### Dashboard Page (`templates/dashboard.html`)
```text
--------------------------------------------------------------------------------
Navbar: AgroPulse                            Home | Dashboard | Compare | About
--------------------------------------------------------------------------------
Welcome, Farmer 🌾
Here’s today’s smart market insight for your crops

[ Card: Crop ]            [ Card: Nearest Mandi ]      [ Card: Best Market Price ]
Wheat                     Indore APMC (5 km)           ₹2250 / quintal

[ Card: Compared ]        [ Card: Recommendation ]     [ Card: Price Trend ]
4 Nearby Mandis           WAIT 3 DAYS (Gain ₹300)      Increasing (3 Days)

                      [ Compare All Markets (Btn) ]  [ Predict Future Price (Btn) ]
--------------------------------------------------------------------------------
Footer
--------------------------------------------------------------------------------
```

#### Prediction Page (`templates/prediction.html`)
```text
--------------------------------------------------------------------------------
Navbar: AgroPulse                             Home | Dashboard | Compare | About
--------------------------------------------------------------------------------
🌾 AI Crop Price Prediction
Get 7-day future price forecasts and smart advice.

[ State: MP v ] [ District: Indore v ] [ Crop: Wheat v ] [ Analyze (Btn) ]

========================== Prediction Output ==========================
[ Recommendation Card ]
Advice: WAIT 3 DAYS
Expected Gain: ₹120/quintal  |  Best Market: Indore APMC
Trend: RISING                |  Confidence: HIGH

[ Chart Card ]
  Price (₹)
   |                .---. (Upper Bound)
   |           .---'
   |      .---*---. (Prediction Line)
   | .---'   /
   |________/________ (Lower Bound)
   +------------------------------ Days
     Today  D1  D2  D3  D4  D5  D6  D7
======================================================================
--------------------------------------------------------------------------------
Footer
--------------------------------------------------------------------------------
```

#### Comparison Page (`templates/comparison.html`)
```text
--------------------------------------------------------------------------------
Navbar: AgroPulse                             Home | Dashboard | Compare | About
--------------------------------------------------------------------------------
Select Crop: [ Wheat v ]  [ Show Prices (Btn) ]

-----------------------------------------------------------------------
Crop  | Mandi Name   | Price (₹/quintal) | Distance | Type | Status
-----------------------------------------------------------------------
Wheat | Dewas APMC   | ₹2250             | 18 km    | APMC | Best (Badge)
Wheat | Indore APMC  | ₹2100             | 5 km     | APMC |
Wheat | Ujjain FPO   | ₹2050             | 32 km    | FPO  |
Wheat | Bhopal APMC  | ₹2000             | 45 km    | APMC |
-----------------------------------------------------------------------

                       [ Sort by Price (Btn) ] [ Sort by Distance (Btn) ]
--------------------------------------------------------------------------------
Footer
--------------------------------------------------------------------------------
```

---

### 3.4 UI/UX Analysis
*   **User Flow Diagram**:
    ```mermaid
    flowchart TD
        A[Guest Access] --> B{Choose Action}
        B -->|Public Lookup| C[Landing / About]
        B -->|Login Required| D[Login Page]
        D -->|Forgot Password| E[Forgot Password Page]
        E -->|Email Link| F[Reset Password Page]
        F --> D
        D -->|Auth Success| G[Farmer Dashboard]
        G -->|Check Forecast| H[Prediction UI]
        G -->|Check Mandis| I[Comparison UI]
        H -->|Authenticated| J[Save Query to DB]
        J --> K[History UI]
    ```
*   **Navigation Flow**:
    *   Global navigation toolbar exists at the header of all views, using the class `navbar`. Active pages are highlighted with the class `active`.
    *   Unauthenticated calls are intercepted by [static/js/utils.js](file:///f:/GitHub/AgroPulse/static/js/utils.js), which redirects users back to `/login?returnTo=currentPath` upon receiving a 401 code.
*   **Information Architecture**:
    *   Shallow navigation hierarchy. All key features (Dashboard, Compare, Prediction, History, About) are accessible within a single click from the navigation header.
*   **UX Strengths**:
    *   Distinct color-coded visual indicator badges (green for rising/high, amber for medium, red for falling/low) simplify raw numbers.
    *   Dropdown values populate dynamically using the dataset to prevent queries for invalid state/district configurations.
*   **UX Weaknesses**:
    *   The SignUp link on the login page triggers a browser alert box instead of rendering a registration screen.
    *   The distance value in the comparison table is hardcoded to static values.

---

### 3.5 Design System

#### Colors
*   **Primary Green**: `#22c55e` (`rgb(34,197,94)`) - Used for primary actions, active navigation states, success cards, and rising trends.
*   **Dark Green**: `#16a34a` (`rgb(22,163,74)`) - Button hover backgrounds.
*   **Base Background**: Slate Gray `#f1f5f9` (`rgb(241,245,249)`) - Page content panels.
*   **Neutral Dark**: Dark Blue `#0f172a` (`rgb(15,23,42)`) - Header navigation bar background.
*   **Text Color**: Dark Charcoal `#1f2933` (`rgb(31,41,51)`) - Body typography.
*   **Muted Text**: Slate Blue `#64748b` (`rgb(100,116,139)`) - Secondary text descriptions.
*   **Alert Success**: Light Green background (`#dcfce7`), Dark Green text (`#166534`).
*   **Alert Danger**: Light Red background (`#fee2e2`), Dark Red text (`#b91c1c`).

#### Typography
*   **Font Family**: `Arial, Helvetica, sans-serif` globally.
*   **Sizes**:
    *   Page Titles (`h1`): `2.2rem` to `3rem`
    *   Section Titles (`h2`): `2.4rem`
    *   Card Titles (`h3` / `h4`): `1.2rem` to `1.5rem`
    *   Standard Body: `1rem`
    *   Badges/Metadata: `0.85rem`
*   **Line Heights**: `1.6` globally.
*   **Font Weights**: Normal (`400`), Medium (`600`), Bold (`700`).

#### Spacing System
*   **Margins**: `10px`, `18px`, `20px`, `30px`, `35px`, `40px`.
*   **Paddings**: `8px`, `10px`, `12px`, `15px`, `20px`, `22px`, `25px`, `30px`, `40px`.
*   **Card Borders**: Border radius values are `6px`, `8px`, `10px`, `14px`, and `16px`.

#### Components
*   **Buttons**:
    *   Class `.login-btn` / `.btn-primary` / `.primary-btn`: Full-width or inline rounded rectangles, padded (`10px` to `14px`), background `#22c55e`, white text. Transitions to `#16a34a` on hover.
    *   Class `.secondary-btn`: Rounded borders, identical coloring.
*   **Inputs**: Rounded borders (`8px`), padded (`12px`), borders `#cbd5e1`. Outline transitions to `#22c55e` on focus.
*   **Cards**: Class `.card`: Background white, padded (`25px`), rounded corners (`16px`), drop shadow `0 10px 25px rgba(0,0,0,0.08)`.
*   **Tables**: Standard HTML layout, `#22c55e` solid green background header row, padded cells (`12px`), alternating white/slate borders.
*   **Alert Box**: Element ID `#alertBox`: Rounded border (`8px`), padded (`12px`), displays error or success based on response class list.

#### Responsive Design
*   Form elements scale to `width: 100%` on screens smaller than `768px`.
*   CSS Grid layouts are configured with the pattern `repeat(auto-fit, minmax(260px, 1fr))` to shift cards into single columns on mobile displays.

### 3.6 Design Recreation Guide
To replicate the AgroPulse interface layout:
1.  Wrap all pages in a global container using body background `#f1f5f9` (except login pages, which use a gradient `linear-gradient(to right, #ecfeff, #f0fdf4)`).
2.  Construct header nav elements with height `#0f172a` and padding `15px 40px`, displaying the text logo on the left and inline routes on the right.
3.  Draw card containers with white backgrounds, border radius `16px`, and drop shadows `rgba(0,0,0,0.08)`.
4.  Style primary buttons using background color `#22c55e` with white font.
5.  Create status badges with rounded borders (`20px`) and color themes matching the current trend (green/red/blue).

---

## 4. Backend Analysis

### 4.1 Backend Architecture
The backend is powered by Flask (configured in [app.py](file:///f:/GitHub/AgroPulse/app.py)), structured around the following layers:
*   **Routes Layer** ([routes/](file:///f:/GitHub/AgroPulse/routes)): Receives incoming client HTTP API requests.
*   **Service Layer** ([services/](file:///f:/GitHub/AgroPulse/services)): Business logic implementations (calculating recommendations and querying predictions cache).
*   **Model Layer** ([models/](file:///f:/GitHub/AgroPulse/models)): MongoDB abstract collections interface.
*   **Database Connector** ([utils/db_connection.py](file:///f:/GitHub/AgroPulse/utils/db_connection.py)): Manages Singleton socket connections to avoid socket leaks.
*   **Validator Layer** ([utils/validators.py](file:///f:/GitHub/AgroPulse/utils/validators.py)): Coerces request payloads and returns format errors.

### 4.2 Request Flow
```text
Client Browser HTTP Request
  │
  ▼
Routes Layer (e.g. routes/prediction_routes.py)
  │
  ▼
Limiter & Session Check Middleware (app.py)
  │
  ▼
Request Body Validation (utils/validators.py)
  │
  ▼
Service Layer Logic (services/prediction_service.py)
  │
  ├─► Predictions Cache Lookup (models/predict.py)
  │
  └─► [Cache Miss] ML Model Inference (ml/predict.py)
        │
        ▼
  Singleton Database Connection Client (utils/db_connection.py)
        │
        ▼
  MongoDB Server Query
        │
        ▼
Response JSON Serialization (utils/helpers.py)
```

---

### 4.3 API Documentation

All endpoints are registered under the `/api/v1` blueprint prefix namespace. Legacy endpoints (prefaced by `/api/`) are redirected to the equivalent `/api/v1/` path using a 308 redirect logic.

#### 1. POST /api/v1/auth/login
*   **Purpose**: Authenticate user credentials and establish session.
*   **Authentication**: None
*   **Rate Limit**: 10 requests per hour
*   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "Password123"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Login successful",
      "user": {
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
    ```
*   **Error Responses**:
    *   `400 Bad Request`: Missing email or password.
    *   `401 Unauthorized`: Invalid credentials, or user email unverified.
    *   `500 Internal Server Error`: Server exception.

#### 2. POST /api/v1/auth/register
*   **Purpose**: Register a new user and trigger verification email link.
*   **Authentication**: None
*   **Rate Limit**: 5 requests per hour
*   **Request Body**:
    ```json
    {
      "name": "John Doe",
      "email": "user@example.com",
      "password": "Password123!"
    }
    ```
*   **Response (201 Created)**:
    ```json
    {
      "success": true,
      "message": "Registration successful. Please verify your email."
    }
    ```
*   **Error Responses**:
    *   `400 Bad Request`: Missing fields, invalid email format, password too short (< 8 chars).
    *   `409 Conflict`: Email already exists.

#### 3. GET /api/v1/auth/verify/\<token\>
*   **Purpose**: Verify the user registration token and redirect to login page.
*   **Authentication**: None
*   **Response (302 Redirect)**: Redirects browser to `/login?verified=1`
*   **Error Responses**:
    *   `400 Bad Request`: Link expired (max-age 24 hours) or signature invalid.
    *   `404 Not Found`: User not found.

#### 4. POST /api/v1/auth/resend-verification
*   **Purpose**: Resend email verification token.
*   **Authentication**: None
*   **Rate Limit**: 3 requests per hour
*   **Request Body**:
    ```json
    {
      "email": "user@example.com"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "If the email is registered and unverified, a new link has been sent."
    }
    ```

#### 5. POST /api/v1/auth/logout
*   **Purpose**: Terminate session cookie state.
*   **Authentication**: None
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Logged out"
    }
    ```

#### 6. POST /api/v1/auth/forgot-password
*   **Purpose**: Generate and email a password reset link token.
*   **Authentication**: None
*   **Rate Limit**: 3 requests per hour
*   **Request Body**:
    ```json
    {
      "email": "user@example.com"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "If that email is registered you will receive a reset link"
    }
    ```

#### 7. POST /api/v1/auth/reset-password
*   **Purpose**: Update password using valid reset token payload.
*   **Authentication**: None
*   **Request Body**:
    ```json
    {
      "token": "token_string",
      "new_password": "NewPassword123!",
      "confirm_password": "NewPassword123!"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Password reset successfully"
    }
    ```
*   **Error Responses**:
    *   `400 Bad Request`: Expired/used link (max-age 1 hour), passwords mismatch, password too short (< 8 chars).

#### 8. GET /api/v1/auth/check
*   **Purpose**: Check session credentials and return user context.
*   **Authentication**: Session cookie
*   **Response (200 OK)**:
    ```json
    {
      "authenticated": true,
      "user": {
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
    ```

#### 9. POST /api/v1/predict
*   **Purpose**: Return 7-day predicted prices and recommendations.
*   **Authentication**: None (saves queries to history if logged in)
*   **Rate Limit**: 30 requests per hour
*   **Request Body**:
    ```json
    {
      "crop": "Wheat",
      "location": "Indore",
      "state": "Madhya Pradesh",
      "quantity": 100
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "predicted_price": 2150.0,
      "predicted_prices": [2150.0, 2170.0, 2185.0, 2200.0, 2210.0, 2225.0, 2240.0],
      "upper_bound": [2230.0, 2250.0, 2265.0, 2280.0, 2290.0, 2305.0, 2320.0],
      "lower_bound": [2070.0, 2090.0, 2105.0, 2120.0, 2130.0, 2145.0, 2160.0],
      "recommendation": "WAIT 3 DAYS",
      "expected_gain": "₹90 / quintal",
      "best_market": "Indore APMC",
      "trend": "rising",
      "confidence": "high",
      "model_type": "machine_learning",
      "matched_crop": "Wheat",
      "matched_district": "Indore",
      "matched_state": "Madhya Pradesh"
    }
    ```
*   **Error Responses**:
    *   `400 Bad Request`: Missing crop or location parameter.

#### 10. GET /api/v1/predict/history
*   **Purpose**: Get user prediction queries history log list.
*   **Authentication**: Required
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": [
        {
          "_id": "60c72b2f9b1d8e2b8c8b4567",
          "crop": "Wheat",
          "state": "Madhya Pradesh",
          "district": "Indore",
          "predicted_prices": [2150, 2170, 2185, 2200, 2210, 2225, 2240],
          "recommendation": "WAIT 3 DAYS",
          "confidence": "high",
          "trend": "rising",
          "created_at": "2026-06-26T18:30:00Z"
        }
      ],
      "total": 1,
      "page": 1,
      "per_page": 5,
      "pages": 1
    }
    ```

#### 11. DELETE /api/v1/predict/history/\<history_id\>
*   **Purpose**: Remove prediction record.
*   **Authentication**: Required
*   **Response (200 OK)**:
    ```json
    {
      "success": true
    }
    ```
*   **Error Responses**:
    *   `404 Not Found`: Record not found.

#### 12. GET /api/v1/predict/model-info (and GET /api/v1/predict/metadata)
*   **Purpose**: Fetch supported states, districts, and crop values.
*   **Authentication**: None
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "ml_available": true,
      "n_states": 2,
      "n_districts": 3,
      "n_crops": 3,
      "supported_states": ["Madhya Pradesh", "Rajasthan"],
      "supported_districts": ["Indore", "Jaipur", "Chittorgarh"],
      "supported_crops": ["Wheat", "Rice", "Cotton"],
      "state_district_mapping": {
        "Madhya Pradesh": ["Indore"],
        "Rajasthan": ["Jaipur", "Chittorgarh"]
      }
    }
    ```

#### 13. POST /api/v1/prices
*   **Purpose**: Fetch current prices, prediction advice, and statistics.
*   **Authentication**: None
*   **Request Body**:
    ```json
    {
      "crop": "Wheat",
      "location": "Indore",
      "quantity": 100
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "currentPrices": [
          {
            "mandi": "Indore APMC",
            "price": 2250.0,
            "district": "Indore",
            "state": "Madhya Pradesh",
            "date": "2026-06-26",
            "min_price": 2200,
            "max_price": 2300,
            "type": "APMC"
          }
        ],
        "prediction": {
          "predictedPrices": [2250.0, 2260.0, 2280.0, 2300.0, 2310.0, 2320.0, 2330.0],
          "trend": "rising",
          "optimalDay": 3,
          "confidence": 0.88,
          "current_price": 2250.0
        },
        "recommendation": {
          "action": "WAIT",
          "message": "Wait 3 days. Price expected to rise by ₹50 (2.2%)",
          "confidence": "MEDIUM",
          "expectedGain": 50.0,
          "gainPercent": 2.22,
          "bestMarket": "Indore APMC",
          "bestPrice": 2250,
          "optimalDay": 3
        },
        "statistics": {
          "average": 2250.0,
          "minimum": 2200,
          "maximum": 2300,
          "change_percent": 1.25
        }
      }
    }
    ```

#### 14. GET /api/v1/prices/current
*   **Purpose**: Get recent raw price listings for a crop.
*   **Authentication**: None
*   **Request Parameters**: `crop`, `location`
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": [
        {
          "mandi": "Indore APMC",
          "price": 2250,
          "district": "Indore",
          "state": "Madhya Pradesh",
          "date": "2026-06-26"
        }
      ],
      "total": 1,
      "page": 1,
      "per_page": 20,
      "pages": 1
    }
    ```

#### 15. GET /api/v1/prices/statistics
*   **Purpose**: Retrieve historical statistics calculations.
*   **Authentication**: None
*   **Request Parameters**: `crop`, `location`
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "average": 2250.0,
        "minimum": 2200,
        "maximum": 2300,
        "change_percent": 1.25
      }
    }
    ```

#### 16. GET /api/v1/markets
*   **Purpose**: Paginate and query market hubs metadata.
*   **Authentication**: None
*   **Request Parameters**: `district`, `type`
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": [
        {
          "name": "Indore APMC",
          "district": "Indore",
          "state": "Madhya Pradesh",
          "type": "APMC",
          "crops_accepted": ["Wheat", "Rice"],
          "timings": "8 AM - 6 PM"
        }
      ],
      "total": 1,
      "page": 1,
      "per_page": 20,
      "pages": 1
    }
    ```

#### 17. GET /api/v1/markets/\<district\>
*   **Purpose**: Query markets in a district.
*   **Authentication**: None
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "markets": [
          {
            "name": "Indore APMC",
            "type": "APMC",
            "contact": { "phone": "0731-2234567" },
            "crops_accepted": ["Wheat"]
          }
        ],
        "count": 1
      }
    }
    ```

#### 18. GET /api/v1/mandi/compare
*   **Purpose**: Fetch crop prices across districts for comparisons.
*   **Authentication**: None
*   **Request Parameters**: `crop`, `lat`, `lon`
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "markets": [
        {
          "market": "Dewas",
          "price": 2250,
          "type": "APMC",
          "distance": "18.2 km"
        }
      ]
    }
    ```

#### 19. POST /api/v1/admin/reload-mandi-data
*   **Purpose**: Force backend to reload updated `mandi_prices.csv` dataset in-memory cache.
*   **Authentication**: Admin (requires `X-Admin-Key` header matching the environment `ADMIN_KEY`)
*   **Request Headers**:
    *   `X-Admin-Key`: `<secret_admin_key>`
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Data reloaded successfully",
      "rows": 1284
    }
    ```
*   **Error Responses**:
    *   `403 Forbidden`: `{"error": "Forbidden", "message": "Invalid or missing admin key"}` (Returned when `X-Admin-Key` header is missing, incorrect, or `ADMIN_KEY` config is unset)

#### 20. GET /health
*   **Purpose**: Verify server connection status, model loaders, and DB ping.
*   **Authentication**: Rate Limit Exempt
*   **Response (200 OK)**:
    ```json
    {
      "status": "ok",
      "model_loaded": true,
      "db_connected": true
    }
    ```

---

### 4.4 Business Logic
*   **Predictions Cache Policy** (configured in [services/prediction_service.py](file:///f:/GitHub/AgroPulse/services/prediction_service.py)):
    When a prediction query is triggered, the system checks if a record exists in the `predictions` cache collection with the matching `crop` and `location` parameters and was created within the last **2 hours**. If a cache record is found, it is returned immediately instead of running scikit-learn model inference.
*   **Model Fallback**:
    If the ML pickle file loader fails or features encoder encounters a mismatch, `fallback_prediction` generates a synthetic distribution centered around ₹2000 (standard deviation of ₹200) with a 7-day trend calculation based on the calendar month.
*   **Data Validation Rules**:
    Validations in [utils/validators.py](file:///f:/GitHub/AgroPulse/utils/validators.py) ensure:
    *   Crops are in the whitelisted list `SUPPORTED_CROPS` defined in `config.py`.
    *   Quantities reside between 0 and 10,000 quintals.

### 4.5 Security Review
*   **Authentication**: Safe password security using `bcrypt.hashpw` with salt. Verification links expire after 24 hours.
*   **Session Security**: Signed session cookies configured with `HttpOnly` and `SameSite=Lax` parameters to prevent XSS and limit CSRF.
*   **Brute-Force Rate Limiting**: Flask-Limiter applies constraints of 10 login operations and 5 registration posts per hour.
*   **Security Vulnerabilities**:
    *   `SECRET_KEY` is fallback set to a hardcoded string in development configurations.
    *   API routes bypass Flask-WTF CSRF tokens on JSON state-changing requests.

---

## 5. Database Analysis

### 5.1 Database Overview
*   **Database Engine**: MongoDB 7.0.
*   **Driver**: PyMongo 4.6.0. No ORM/ODM mapper is configured. Raw JSON query dictionary structures are passed directly.
*   **Connection Pattern**: Central singleton class managed via `db_connection.py` containing connection verification helpers.

### 5.2 Entity Relationship Diagram
```mermaid
erDiagram
    USERS ||--o{ PREDICTION_HISTORY : saves
    MARKETS ||--o{ PRICES : hosts
    PRICES }|--|| PREDICTIONS : cached_from
```

### 5.3 Collections

#### 1. users
*   **Purpose**: Stores user profile data, credentials, and verification state.
*   **Schema**:

| Field Name | BSON Type | Nullable | Default | Description |
|---|---|---|---|---|
| `_id` | ObjectId | No | Auto Generated | Primary Key |
| `name` | String | No | None | User name |
| `email` | String | No | None | Login email (Unique Index) |
| `password` | Binary/String | No | None | Bcrypt hashed string |
| `verified` | Boolean | No | `False` | Email verification flag |
| `created_at` | Date | No | `datetime.utcnow()` | Registration date |
| `password_reset_version` | Int32 | Yes | `0` | Password invalidation token version tracker |

*   **Indexes**:
    *   `email` (Ascending), Unique.

#### 2. prices
*   **Purpose**: Stores actual historical commodity prices reported by local mandis.
*   **Schema**:

| Field Name | BSON Type | Nullable | Default | Description |
|---|---|---|---|---|
| `_id` | ObjectId | No | Auto Generated | Primary Key |
| `crop` | String | No | None | Commodity name |
| `mandi_name` | String | No | None | Market branch name |
| `district` | String | No | None | Market district location |
| `state` | String | No | None | Market state location |
| `modal_price` | Double / Int32 | No | None | Most common transaction price |
| `min_price` | Double / Int32 | No | None | Lowest price registered |
| `max_price` | Double / Int32 | No | None | Highest price registered |
| `date` | String | No | None | Record date format `YYYY-MM-DD` |
| `arrival_quantity` | Double / Int32 | Yes | None | Volume traded |
| `type` | String | Yes | `"APMC"` | Market category (APMC/FPO) |
| `created_at` | Date | No | `datetime.now()` | Record creation date |

*   **Indexes**:
    *   Compound Index: `crop` (Ascending), `district` (Ascending), `state` (Ascending).
    *   Single Index: `date` (Descending).
    *   Compound Index: `crop` (Ascending), `date` (Descending).

#### 3. markets
*   **Purpose**: Stores contact and facility metadata for various agricultural trading hubs.
*   **Schema**:

| Field Name | BSON Type | Nullable | Default | Description |
|---|---|---|---|---|
| `_id` | ObjectId | No | Auto Generated | Primary Key |
| `mandi_name` | String | No | None | Unique Mandi Name |
| `district` | String | No | None | Mandi district |
| `state` | String | No | None | Mandi state |
| `type` | String | No | `"APMC"` | Category tag |
| `location` | Document | Yes | None | GeoJSON Point `[longitude, latitude]` |
| `contact` | Document | Yes | None | Phone and email info |
| `crops_accepted` | Array (String) | Yes | None | List of crops allowed |
| `timings` | String | Yes | None | Operational hours |
| `facilities` | Array (String) | Yes | None | Services (e.g. storage, testing) |

*   **Indexes**:
    *   Single Index: `district` (Ascending).
    *   Single Index: `state` (Ascending).

#### 4. predictions
*   **Purpose**: Implements cache storage to reduce model calculation overhead.
*   **Schema**:

| Field Name | BSON Type | Nullable | Default | Description |
|---|---|---|---|---|
| `_id` | ObjectId | No | Auto Generated | Primary Key |
| `crop` | String | No | None | Commodity name |
| `location` | String | No | None | District name |
| `predicted_prices` | Array (Double) | No | None | 7-day predicted values |
| `trend` | String | No | `"stable"` | Price trajectory label |
| `optimal_day` | Int32 | No | `1` | Day showing maximum profit |
| `confidence` | String | No | `"medium"` | Model validation metrics score |
| `current_price` | Double | No | None | Anchor price today |
| `created_at` | Date | No | `datetime.now()` | Prediction date |

*   **Indexes**:
    *   Compound Index: `crop` (Ascending), `location` (Ascending), `created_at` (Descending).

#### 5. prediction_history
*   **Purpose**: Stores historical prediction records queried by verified users.
*   **Schema**:

| Field Name | BSON Type | Nullable | Default | Description |
|---|---|---|---|---|
| `_id` | ObjectId | No | Auto Generated | Primary Key |
| `user_id` | String / ObjectId | No | None | Owner user ID reference |
| `crop` | String | No | None | Commodity name |
| `state` | String | No | None | State name |
| `district` | String | No | None | District name |
| `quantity` | Double | Yes | None | Volume parameter |
| `predicted_prices` | Array (Double) | No | None | Forecast values array |
| `upper_bound` | Array (Double) | No | None | Upper MAE boundary array |
| `lower_bound` | Array (Double) | No | None | Lower MAE boundary array |
| `recommendation` | String | Yes | None | Action advice string |
| `expected_gain` | String | Yes | None | Calculated profit difference |
| `best_market` | String | Yes | None | Recommended market |
| `confidence` | String | Yes | None | High/Medium/Low label |
| `trend` | String | Yes | None | Trajectory direction label |
| `created_at` | Date | No | `datetime.utcnow()` | Record timestamp |

*   **Indexes**:
    *   Single Index: `user_id` (Ascending).
    *   Compound Index: `user_id` (Ascending), `created_at` (Descending).
    *   Single Index: `created_at` (Descending).

### 5.4 Data Flow
Data flows through the system as follows:
```text
Ingestion: Input CSV/Agmarknet API -> scripts/update_mandi_data.py -> ml/data/mandi_prices.csv
Training: CSV Dataset -> ml/data_pipeline.py (Standardize & clean) -> ml/train_model.py -> Model Pickles (.pkl)
Execution: API Post -> routes/prediction_routes.py -> predict_price() -> Random Forest Predict -> MongoDB history
```

### 5.5 Migrations
AgroPulse does not use a database migration tool (such as Alembic). Collections are generated dynamically on startup during insertion processes. Secondary database collection indexes are verified and created on server startup by calling `create_indexes()` inside [scripts/create_indexes.py](file:///f:/GitHub/AgroPulse/scripts/create_indexes.py).

---

## 6. Authentication & Authorization

### Login Flow
1.  Client POSTs credentials to `/api/v1/auth/login`.
2.  Backend queries `users` by email.
3.  Passwords are checked using `bcrypt.checkpw()`.
4.  User must have `verified == True`; otherwise, login fails.
5.  On success, the session variables `user_id`, `email`, and `name` are set.

### Registration Flow
1.  Client POSTs registration payload to `/api/v1/auth/register`.
2.  Input format, email validation, and password length are verified.
3.  Password is hashed using `bcrypt.hashpw(password, bcrypt.gensalt())`.
4.  User document is inserted into MongoDB with `verified = False`.
5.  Verification token is generated via `URLSafeTimedSerializer(SECRET_KEY).dumps(email, salt='email-verify')`.
6.  Verification link is emailed to the user (or logged as warning if SMTP details are missing).

### Password Reset Flow
1.  Client POSTs email to `/api/v1/auth/forgot-password`.
2.  If the user document exists and is verified, the system generates a timed token mapping `{email, version}`.
3.  Email containing the reset link (`/password-reset/<token>`) is dispatched.
4.  User navigates to the reset page and POSTs the new password to `/api/v1/auth/reset-password`.
5.  The backend verifies the token and version. Upon validation, the password is updated, and the version field is incremented by 1 to invalidate old links.

### Session Handling
Sessions are handled via signed HTTP cookies (`session['user_id']`). Session lifetime defaults to 7 days (`PERMANENT_SESSION_LIFETIME = timedelta(days=7)`).

### Permission Matrix

| Route Endpoint | Authenticated | Unauthenticated | Admin/Roles |
|---|---|---|---|
| `POST /api/v1/auth/login` | Allowed | Allowed | N/A |
| `POST /api/v1/auth/register` | Allowed | Allowed | N/A |
| `POST /api/v1/predict` | Saves history | Runs predictions only | N/A |
| `GET /api/v1/predict/history` | Returns logs | Blocks (401 Redirect) | N/A |
| `DELETE /api/v1/predict/history/<id>` | Deletes log | Blocks (401 Redirect) | N/A |
| `GET /api/v1/prices/current` | Allowed | Allowed | N/A |
| `GET /api/v1/mandi/compare` | Allowed | Allowed | N/A |
| `POST /api/v1/admin/reload-mandi-data` | Blocks (403 Forbidden) | Blocks (403 Forbidden) | Allowed (Requires valid `X-Admin-Key` header) |

---

## 7. Third-Party Integrations

### MongoDB
*   **Purpose**: Centralized storage for user profiles, historical prices, and prediction logs.
*   **Config**: Configured using `MONGO_URI` and `DATABASE_NAME` in config profiles.
*   **Failures**: Handled via startup exceptions inside [utils/db_connection.py](file:///f:/GitHub/AgroPulse/utils/db_connection.py).

### Redis
*   **Purpose**: Flask-Limiter backend storage.
*   **Config**: Configured via `REDIS_URL`. Defaults to local in-memory storage (`memory://`) if Redis is unavailable.

### Flask-Mail
*   **Purpose**: Email delivery for registration and password resets.
*   **Config**: Configured via SMTP settings.
*   **Failures**: If sending fails, the system logs the link in `agropulse.log` so the user can verify accounts locally.

### CDNs (Content Delivery Networks)
*   **Bootstrap v5.3.2**: CSS and JS layout libraries.
*   **Chart.js**: Graph generation libraries in predictions.
*   **FontAwesome v6.4.0**: Icons.

---

## 8. Deployment Architecture

### Environment Variables
*   `SECRET_KEY`: Flask encryption key.
*   `MONGO_URI` / `DATABASE_NAME`: Database target.
*   `REDIS_URL`: Optional caching layer.
*   `BASE_URL`: Used to build absolute token links.
*   `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`: Mail server credentials.
*   `FLASK_ENV`: Deployment mode (`development`, `testing`, `production`).

### Build Process & Docker Setup
The project is containerized using `Dockerfile` and `docker-compose.yml`. Gunicorn serves the Flask application.

```mermaid
flowchart TD
    Ingress[Internet / Port 80] -->|HTTP Proxy| WebContainer[Web Container: Gunicorn App Port 8000]
    WebContainer <-->|Internal network| MongoContainer[Mongo Container: MongoDB Port 27017]
    WebContainer <-->|Rate limiting checks| RedisContainer[Redis Container: Cache Port 6379]
    MongoContainer -->|Persistent Volume| DBVolume[(MongoDB Data Volume)]
```

### GitHub Actions CI/CD
We have integrated two GitHub Actions workflows under `.github/workflows/`:
1.  **CI Pipeline (`ci.yml`)**: Triggered on push to `main` and `develop` and on pull requests to `main`. It sets up a Python 3.11 environment, handles dependency caching, spins up a MongoDB 7.0 service container for testing, runs the `pytest` test suite, and uploads test log artifacts.
2.  **Deploy Check (`deploy-check.yml`)**: Triggered on push to `main`. It tests the Dockerfile build, verifies the existence of the `/health` endpoint in `app.py`, and checks if `.env.example` contains all required variables.

### Render.com Deployment
The application is pre-configured for Render.com deployment using `render.yaml` and `runtime.txt` (targeting python-3.11.0). The configuration:
*   Runs a build command that installs dependencies, cleans the data, retrains the ML models dynamically to prevent losing model pickles due to Render's ephemeral filesystem, and sets up database indexes.
*   Runs a dynamic port-binding start command with Gunicorn (`gunicorn --workers 3 --bind 0.0.0.0:$PORT "app:create_app()"`).

---

## 9. Code Quality Review

*   **Code Smells & Mismatches**:
    *   **Dropdown Overwrite Bug**: In [comparison.html](file:///f:/GitHub/AgroPulse/templates/comparison.html#L389-L393), the `window.onload` script triggers `loadCrops()` which populates the crop filter dropdown using a static client-side crop array. This overwrites the dynamic API-backed crop listing populated on `DOMContentLoaded` by [prediction_metadata.js](file:///f:/GitHub/AgroPulse/static/js/prediction_metadata.js).
    *   **Missing Script Tag in Landing**: In [index.html](file:///f:/GitHub/AgroPulse/templates/index.html#L138-L139), there is a syntax error where the opening `<script>` tag is omitted before the `/* ================= GLOBAL DATA ================= */` comment, preventing the dropdown population script from running.
    *   **Import-Time Model Loading**: Model pickle files are imported on start inside [prediction_routes.py](file:///f:/GitHub/AgroPulse/routes/prediction_routes.py). If files are missing, errors are caught via broad exceptions.
*   **Technical Debt**:
    *   Location services in client comparisons use hardcoded distance mock offsets if coordinate inputs are absent.
*   **Performance Concerns**:
    *   The `routes/mandi_routes.py` previously read the raw CSV prices dataset on every query. This has been resolved by loading the dataframe into the in-memory cache (`app.mandi_data`) once on server startup.
*   **Refactoring Opportunities**:
    *   Consolidate all JSON response templates to utilize the centralized `format_response` method.
    *   Migrate all CSV prices data into the MongoDB database and define compound queries.

---

## 10. Rebuild Guide

To recreate the AgroPulse project from scratch:

### 1. Database Initialization
1.  Set up MongoDB and Redis databases.
2.  Run `create_indexes.py` to create collection indexes on `users`, `prices`, `markets`, and `predictions`.
3.  Ingest sample records using the population script:
    ```bash
    python scripts/populate_db.py
    ```

### 2. Machine Learning Pipeline
1.  Process and clean raw dataset data:
    ```bash
    python ml/data_pipeline.py
    ```
2.  Train the Random Forest regression model to output model pickles:
    ```bash
    python ml/train_model.py
    ```

### 3. Backend Implementation
1.  Initialize the Flask factory, configure CORS rules, and add session parameter settings.
2.  Set up password security using `bcrypt`.
3.  Register Blueprints routing endpoints under the `/api/v1` namespace.
4.  Configure the predictions caching policy inside the predictions service.

### 4. Frontend Implementation
1.  Implement Jinja2 templates, utilizing dynamic endpoints mappings.
2.  Render price predictions using Chart.js, referencing predicted price coordinates and confidence intervals.
3.  Use the helper wrapper `window.fetchJSON` for API requests.

### 5. Automated Tests Setup
1.  Execute testing verification locally using `pytest`:
    ```bash
    FLASK_ENV=testing pytest tests/ -v
    ```

---

## 11. Missing Documentation & Risks

*   **Undocumented Features**:
    *   **Admin Reload API**: The endpoint `POST /api/v1/admin/reload-mandi-data` is not exposed in public documentations. It allows administrators to refresh the in-memory cache with updated CSV data, secured with a custom header key.
    *   **Admin Key Config**: The deployment variable `ADMIN_KEY` defined in `render.yaml` and `.env` is loaded by the application config and validates all reload endpoints requests.
*   **Assumptions**:
    *   Statistical operations assume the MongoDB database is pre-populated with historical records.
    *   ML features must match the shape of encoders built during training.
*   **Risks**:
    *   POST endpoints are exempt from standard form CSRF checks, relying on strict CORS whitelist checks.

---

## 12. Final Deliverables

1.  **Full Technical Specification**: Detailed architectural flows, service maps, and schemas provided in Sections 2, 4, and 5.
2.  **Product Requirement Document (PRD)**: Purpose, target users, and workflow detailed in Section 1.
3.  **System Design Document**: Architectural flow and Docker configs in Sections 2 and 8.
4.  **API Documentation**: Endpoint parameters and payloads mapped in Section 4.3.
5.  **Database Documentation**: Collections schemas and indexes detailed in Section 5.
6.  **Design System Documentation**: Colors, font families, and sizes mapped in Section 3.5.
7.  **Mermaid Architecture Diagrams**: Included in Section 2 and Section 8.
8.  **ERD Diagrams**: Collection connections mapped in Section 5.2.
9.  **User Flow Diagrams**: Screen flows mapped in Section 3.4.
10. **Feature Inventory**: Main capabilities listed in Section 1.