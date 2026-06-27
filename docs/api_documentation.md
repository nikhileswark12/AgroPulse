# API Specification - AgroPulse

This document maps all backend endpoints registered under the `/api/v1` namespace.

---

## 1. Authentication Service

### 1.1 POST /api/v1/auth/login
Authenticates user login credentials and creates a session cookie.

- **Request Headers**:
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "email": "string (email)",
    "password": "string (min 8 chars)"
  }
  ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "success": true,
      "message": "Login successful",
      "user": {
        "email": "user@example.com",
        "name": "Ram Singh"
      }
    }
    ```
  - **400 Bad Request**: Missing email or password.
  - **401 Unauthorized**: Invalid email/password, or email unverified.

### 1.2 POST /api/v1/auth/register
Registers a new user and sends an email verification link.

- **Request Body**:
  ```json
  {
    "name": "string",
    "email": "string",
    "password": "string (min 8 chars)"
  }
  ```
- **Responses**:
  - **201 Created**:
    ```json
    {
      "success": true,
      "message": "Registration successful. Please verify your email."
    }
    ```
  - **409 Conflict**: Email already exists.

### 1.3 GET /api/v1/auth/verify/<token>
Validates the signup email token.
- **Parameters**: `token` (path, string)
- **Responses**:
  - **302 Found**: Redirects to `/login?verified=1`.
  - **400 Bad Request**: Token signature is invalid or expired.

---

## 2. Prediction Service

### 2.1 POST /api/v1/predict
Generates a 7-day crop price forecast.

- **Request Body**:
  ```json
  {
    "crop": "string (required)",
    "location": "string (required, district)",
    "state": "string (optional)",
    "quantity": "number (optional)"
  }
  ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "success": true,
      "predicted_price": 2200.0,
      "predicted_prices": [2200.0, 2210.0, 2225.0, 2235.0, 2250.0, 2260.0, 2270.0],
      "upper_bound": [2280.0, 2290.0, 2305.0, 2315.0, 2330.0, 2340.0, 2350.0],
      "lower_bound": [2120.0, 2130.0, 2145.0, 2155.0, 2170.0, 2180.0, 2190.0],
      "recommendation": "WAIT 3 DAYS",
      "expected_gain": "₹70 / quintal",
      "best_market": "Indore APMC",
      "trend": "rising",
      "confidence": "high",
      "model_type": "machine_learning",
      "matched_crop": "Wheat",
      "matched_district": "Indore",
      "matched_state": "Madhya Pradesh"
    }
    ```

### 2.2 GET /api/v1/predict/history
Retrieves a paginated list of predictions requested by the logged-in user.

- **Query Parameters**:
  - `page`: default 1
  - `per_page`: default 20 (max 100)
- **Responses**:
  - **200 OK**:
    ```json
    {
      "success": true,
      "data": [],
      "total": 0,
      "page": 1,
      "per_page": 20,
      "pages": 0
    }
    ```
  - **401 Unauthorized**: User is not logged in.
