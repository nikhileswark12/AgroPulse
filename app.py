import os
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize limiter globally so it can be imported in routes
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['200 per hour']
)

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

    # Initialize PyMongo
    mongo_uri = app.config.get('MONGO_URI', os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'))
    try:
        mongo_client = MongoClient(mongo_uri)
        mongo_client.admin.command('ping')
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"MongoDB connection failed on startup: {e}")
        mongo_client = MongoClient(mongo_uri)
        
    db = mongo_client[app.config.get('DATABASE_NAME', 'agropulse')]
    app.config['MONGO_DB'] = db

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

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(prediction_bp, url_prefix='/api')
    app.register_blueprint(mandi_bp, url_prefix='/api')
    app.register_blueprint(price_bp, url_prefix='/api')
    app.register_blueprint(market_bp, url_prefix='/api')

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

    # Health check route
    @app.route('/health')
    @limiter.exempt
    def health_check():
        model_loaded = os.path.exists('ml/trained_model.pkl') or os.path.exists('ml/models/price_model.pkl')
        db_connected = False
        try:
            mongo_client.admin.command('ping')
            db_connected = True
        except ConnectionFailure:
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
    app.run(debug=os.environ.get('FLASK_ENV') == 'development')
