# AgroPulse - Real-Time Crop Price Visibility Platform

## Project Overview

AgroPulse is a web-based platform that aggregates real-time market data from multiple sources and uses machine learning to predict future price trends, empowering farmers with data-driven decision making.

## Tech Stack

- **Backend**: Python 3.8+, Flask
- **Database**: MongoDB
- **ML**: Scikit-learn, Pandas, NumPy
- **Frontend**: HTML, CSS, JavaScript, Bootstrap, Chart.js

## Project Structure

```
agropulse/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
│
├── models/                   # Database models
│   ├── price.py
│   ├── market.py
│   └── prediction.py
│
├── routes/                   # API endpoints
│   ├── price_routes.py
│   ├── market_routes.py
│   └── prediction_routes.py
│
├── services/                 # Business logic
│   ├── price_service.py
│   ├── prediction_service.py
│   └── recommendation_service.py
│
├── ml/                       # Machine Learning
│   ├── train_model.py
│   └── predict.py
│
├── utils/                    # Helper utilities
│   ├── db_connection.py
│   ├── validators.py
│   └── helpers.py
│
├── static/                   # Frontend files
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                # HTML templates
│   ├── index.html
│   ├── dashboard.html
│   ├── comparison.html
│   ├── prediction.html
│   ├── how-it-works.html
│   └── about.html
│
└── scripts/                  # Utility scripts
    └── populate_db.py
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MongoDB 4.4 or higher
- pip (Python package manager)

### Step 1: Extract Project Files

```bash
# Extract the project to your preferred location
cd /path/to/agropulse
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start MongoDB

**Windows:**

```bash
mongod
```

**Linux/Mac:**

```bash
sudo systemctl start mongodb
# or
brew services start mongodb-community
```

### Step 4: Configure Environment Variables

Create a `.env` file based on the template provided:

```bash
cp .env.example .env
```

Edit `.env` with your settings (default values work for localhost).

### Step 5: Populate Database with Sample Data

```bash
cd scripts
python populate_db.py
```

This will create:

- 90 days of historical price data
- 5 markets across Madhya Pradesh
- 5 crops (Wheat, Rice, Soybean, Cotton, Corn)

### Step 6: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Accessing the Application

### Web Interface

Open your browser and navigate to:

- **Home**: <http://localhost:5000>
- **Dashboard**: <http://localhost:5000/dashboard>
- **Comparison**: <http://localhost:5000/comparison>
- **Prediction**: <http://localhost:5000/prediction>

### API Endpoints

#### Get Prices & Recommendation

```bash
POST http://localhost:5000/api/prices
Content-Type: application/json

{
  "crop": "Wheat",
  "location": "Indore",
  "quantity": 100
}
```

#### Get Current Prices Only

```bash
GET http://localhost:5000/api/prices/current?crop=Wheat&location=Indore
```

#### Get Price Prediction

```bash
POST http://localhost:5000/api/predict
Content-Type: application/json

{
  "crop": "Wheat",
  "location": "Indore",
  "days": 7
}
```

#### Get Markets

```bash
GET http://localhost:5000/api/markets
GET http://localhost:5000/api/markets?district=Indore
GET http://localhost:5000/api/markets?type=APMC
```

## Testing the Application

### Sample Test Queries

1. **Search Wheat prices in Indore**
   - Crop: Wheat
   - Location: Indore
   - Expected: Current prices + 7-day prediction + recommendation

2. **Search Soybean prices in Dewas**
   - Crop: Soybean
   - Location: Dewas
   - Expected: Multiple market prices + trend analysis

## Project Features

### Implemented Features ✓

- Multi-source price aggregation
- Real-time price comparison
- ML-powered 7-day price prediction (Linear Regression)
- Smart sell/wait recommendations
- Price statistics and trends
- Market comparison
- RESTful API
- Responsive web interface

### Supported Crops

- Wheat
- Rice
- Soybean
- Cotton
- Corn
- Chickpea
- Mustard
- Sugarcane
- Groundnut
- Onion

### Supported Regions

Currently: Madhya Pradesh (Indore, Dewas, Ujjain, Bhopal, Jabalpur)

## ML Model Details

- **Algorithm**: Linear Regression
- **Features**: Historical prices, seasonal patterns, day of week
- **Training Data**: 90 days of historical prices
- **Accuracy**: ~82% R² score
- **Prediction Range**: 7 days ahead
- **Update Frequency**: On-demand with 2-hour cache

## Troubleshooting

### MongoDB Connection Error

```
Error: Failed to connect to MongoDB
```

**Solution**: Ensure MongoDB is running on port 27017

### No Price Data Found

```
Error: No price data found for {crop} in {location}
```

**Solution**: Run `python scripts/populate_db.py` to populate sample data

### Module Import Error

```
ModuleNotFoundError: No module named 'flask'
```

**Solution**: Install dependencies: `pip install -r requirements.txt`

## Development Team

- **Team Lead**: Kavuru Nikhileswar
- **Institute**: Parul Institute of Engineering & Technology
- **Track**: Web 2.0

## License

This is a hackathon project created for educational purposes.

## Support

For issues or questions, please check the documentation or create an issue in the project repository.
