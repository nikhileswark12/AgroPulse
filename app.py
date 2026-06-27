import os
import sys
if __name__ == '__main__':
    sys.modules['app'] = sys.modules[__name__]
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd

# Initialize limiter globally so it can be imported in routes
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['200 per hour']
)

from flask_wtf.csrf import CSRFProtect, CSRFError
csrf = CSRFProtect()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    load_dotenv()

    app = Flask(__name__)
    
    # Load config based on config_name
    config_module = f"config.{config_name.capitalize()}Config"
    try:
        app.config.from_object(config_module)
    except Exception:
        app.config.from_object('config.Config')

    from utils.logger import configure_logging, get_logger
    configure_logging(app)
    logger = get_logger('startup')
    logger.info(f"Starting application in {os.environ.get('FLASK_ENV', 'development')} mode")

    model_loaded = os.path.exists('ml/trained_model.pkl') or os.path.exists('ml/models/price_model.pkl')
    logger.info(f"ML model file found: {model_loaded}")

    # Initialize PyMongo via central db_connection
    from utils.db_connection import db, get_db
    try:
        db.connect()
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"MongoDB connection failed on startup: {e}")

    # Load Mandi Data into memory
    try:
        df = pd.read_csv('ml/data/mandi_prices.csv')
        df.columns = [c.lower().strip() for c in df.columns]
        if 'crop' in df.columns:
            df['crop'] = df['crop'].astype(str).str.strip().str.title()
        if 'district' in df.columns:
            df['district'] = df['district'].astype(str).str.strip().str.title()
        if 'state' in df.columns:
            df['state'] = df['state'].astype(str).str.strip().str.title()
        app.mandi_data = df
        logger.info(f"Mandi data loaded: {len(df)} rows")
    except Exception as e:
        app.mandi_data = None
        logger.warning(f"Failed to load mandi data: {e}")

    # Initialize indexes
    try:
        from scripts.create_indexes import create_indexes
        create_indexes()
    except Exception as e:
        logger.warning(f"Failed to verify indexes during startup: {e}")

    # Flask-CORS
    cors_origins = app.config.get('CORS_ORIGINS', 'http://localhost:5000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)

    # Flask-Limiter
    app.config['RATELIMIT_STORAGE_URI'] = app.config.get('REDIS_URL', 'memory://')
    limiter.init_app(app)

    # Flask-WTF CSRF
    csrf.init_app(app)
    
    # Flask-Mail
    from flask_mail import Mail
    mail = Mail(app)
    app.config['MAIL'] = mail

    # Session security flags
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = app.config.get('FLASK_ENV') == 'production'

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.prediction_routes import prediction_bp
    from routes.mandi_routes import mandi_bp
    from routes.price_routes import price_bp
    from routes.market_routes import market_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(prediction_bp, url_prefix='/api/v1')
    app.register_blueprint(mandi_bp, url_prefix='/api/v1')
    app.register_blueprint(price_bp, url_prefix='/api/v1')
    app.register_blueprint(market_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/api/v1')

    # Backward compatible redirects
    from flask import redirect
    def redirect_to_v1(*args, **kwargs):
        # request.full_path includes query params if they exist
        new_path = request.path.replace('/api/', '/api/v1/', 1)
        if request.query_string:
            new_path = f"{new_path}?{request.query_string.decode('utf-8')}"
        return redirect(new_path, code=308)

    legacy_routes = [
        '/api/auth/login', '/api/auth/register', '/api/auth/verify/<token>',
        '/api/auth/logout', '/api/auth/check', '/api/auth/forgot-password',
        '/api/auth/reset-password', '/api/auth/resend-verification',
        '/api/predict', '/api/predict/history', '/api/predict/history/<history_id>',
        '/api/predict/model-info', '/api/predict/metadata',
        '/api/prices', '/api/prices/current', '/api/prices/statistics',
        '/api/markets', '/api/markets/<district>', '/api/mandi/compare'
    ]
    
    for idx, route in enumerate(legacy_routes):
        app.add_url_rule(
            route, 
            endpoint=f"legacy_{idx}", 
            view_func=redirect_to_v1, 
            methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        )

    @app.after_request
    def add_api_version_header(response):
        if request.path.startswith('/api/v1/'):
            response.headers['API-Version'] = 'v1'
        return response

    from utils.helpers import validate_origin
    @app.before_request
    def validate_api_origin():
        if request.path.startswith('/api/v1/') and request.method in ['POST', 'DELETE', 'PUT', 'PATCH']:
            if app.testing or (app.config.get('FLASK_ENV') == 'development' and request.remote_addr == '127.0.0.1'):
                return
            
            allowed_origins = app.config.get('CORS_ORIGINS', 'http://localhost:5000').split(',')
            if not validate_origin(request, allowed_origins):
                return jsonify({"error": "Forbidden", "message": "Invalid request origin"}), 403

    # Global error handlers
    def render_error(error, code):
        if request.path.startswith('/api'):
            return jsonify({"error": str(error)}), code
        try:
            return render_template(f'{code}.html', error=error), code
        except Exception:
            return f"<h1>{code} - {error.name if hasattr(error, 'name') else 'Error'}</h1>", code

    @app.errorhandler(400)
    def bad_request(error):
        return render_error(error, 400)

    @app.errorhandler(401)
    def unauthorized(error):
        return render_error(error, 401)

    @app.errorhandler(404)
    def not_found(error):
        return render_error(error, 404)

    @app.errorhandler(429)
    def too_many_requests(error):
        return render_error(error, 429)

    @app.errorhandler(500)
    def internal_error(error):
        return render_error(error, 500)
        
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify({"error": "CSRF validation failed", "message": "Please refresh the page and try again"}), 400

    @app.route('/health')
    @limiter.exempt
    def health_check():
        model_loaded = os.path.exists('ml/trained_model.pkl') or os.path.exists('ml/models/price_model.pkl')
        db_connected = False
        try:
            from utils.db_connection import db
            if db._client:
                db._client.admin.command('ping')
                db_connected = True
        except Exception:
            pass
            
        return jsonify({
            "status": "ok",
            "model_loaded": model_loaded,
            "db_connected": db_connected
        })

    # Page Routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return_to = request.args.get('returnTo', '/dashboard')
        if not return_to.startswith('/') or return_to.startswith('//'):
            return_to = '/dashboard'
        return render_template('login.html', return_to=return_to)

    @app.route('/forgot-password')
    def forgot_password():
        return render_template('forgot_password.html')

    @app.route('/password-reset/<token>')
    def password_reset(token):
        return render_template('reset_password.html', token=token)

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

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_ENV') == 'development')
