from flask import Flask, render_template
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

# ============================================================
# INITIALIZE FLASK APP
# ============================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'your-secret-key-change-in-production'
)

# ============================================================
# INITIALIZE MONGODB
# ============================================================

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
mongo_client = MongoClient(mongo_uri)
db = mongo_client['agropulse']

# 🔥 Store DB in app config (avoids circular imports)
app.config['MONGO_DB'] = db

# ============================================================
# REGISTER BLUEPRINTS (AFTER DB INIT)
# ============================================================

from routes.prediction_routes import prediction_bp
from routes.auth_routes import auth_bp

app.register_blueprint(prediction_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')


from routes.mandi_routes import mandi_bp
app.register_blueprint(mandi_bp, url_prefix="/api")


# ============================================================
# PAGE ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/prediction')
def prediction():
    return render_template('prediction.html')


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/comparison')
def comparison():
    return render_template('comparison.html')


@app.route('/about')
def about():
    return render_template('about.html')


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return "<h1>404 - Page Not Found</h1>", 404


@app.errorhandler(500)
def internal_error(error):
    return "<h1>500 - Internal Server Error</h1>", 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🌾 AgroPulse Server Starting...")
    print("=" * 60)
    print("📊 MongoDB: Connected")
    print("🚀 Server: http://localhost:5000")
    print("📍 Prediction API: http://localhost:5000/api/predict")
    print("📜 History API: http://localhost:5000/api/predict/history")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
