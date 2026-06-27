# Database Schema & Index Documentation - AgroPulse

AgroPulse utilizes **MongoDB** as its primary document datastore. 

---

## 1. Index Architecture
Indexes are configured programmatically inside [scripts/create_indexes.py](file:///f:/GitHub/AgroPulse/scripts/create_indexes.py) to optimize query performance and enforce unique fields.

### 1.1 `users` collection indexes
- `email` (Ascending) -> **Unique** (Enforces single-account registration).

### 1.2 `prediction_history` collection indexes
- `user_id` (Ascending) -> Speeds up lookups on a user's logs.
- Compound: `user_id` (Ascending), `created_at` (Descending) -> Speeds up paginated queries sorted by date.
- `created_at` (Descending) -> Optimized sorting on global logs.

### 1.3 `prices` collection indexes
- Compound: `crop` (Ascending), `district` (Ascending), `state` (Ascending) -> Accelerates target market calculations.
- `date` (Descending) -> Speeds up rolling average queries.
- Compound: `crop` (Ascending), `date` (Descending) -> Fast historical checks for specific crops.

---

## 2. Collection Definitions

### 2.1 Collection: `users`
Stores credentials, verification status, and password version tokens.
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "binary (bcrypt hash)",
  "verified": "boolean (default false)",
  "created_at": "date (default datetime.utcnow())",
  "password_reset_version": "int (default 0)"
}
```

### 2.2 Collection: `prices`
Stores historical crop values reported across APMCs and FPOs.
```json
{
  "_id": "ObjectId",
  "crop": "string",
  "mandi_name": "string",
  "district": "string",
  "state": "string",
  "modal_price": "double",
  "min_price": "double",
  "max_price": "double",
  "date": "string (format YYYY-MM-DD)",
  "arrival_quantity": "double",
  "type": "string (APMC / FPO)",
  "created_at": "date"
}
```
