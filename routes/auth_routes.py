import re
import bcrypt
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app, redirect
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from app import limiter

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def get_db():
    return current_app.config['MONGO_DB']

def send_verification_email(email, token):
    try:
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        verify_link = f"{base_url}/api/auth/verify/{token}"
        
        mail = current_app.config.get('MAIL')
        if mail:
            msg = Message(
                subject='Verify your AgroPulse account',
                recipients=[email],
                body=f'Please click the following link to verify your account: {verify_link}'
            )
            mail.send(msg)
            logger.info(f"Verification email sent to {email}")
        else:
            logger.warning(f"Verification link (mail not configured): {verify_link}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        # Log the link as fallback
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        verify_link = f"{base_url}/api/auth/verify/{token}"
        logger.warning(f"Verification link (fallback): {verify_link}")

# ===================== LOGIN =====================
@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit('10 per hour')
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400

        db = get_db()
        user = db.users.find_one({'email': email})

        if not user:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        # Check password
        stored_hash = user['password']
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
            
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        if not user.get('verified', False):
            return jsonify({'success': False, 'message': 'Please verify your email before logging in'}), 401

        session.clear()
        session['user_id'] = str(user['_id'])
        session['email'] = user['email']
        session['name'] = user.get('name', '')
        session.permanent = True

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': user['email'],
                'name': user.get('name', '')
            }
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ===================== REGISTER =====================
@auth_bp.route('/auth/register', methods=['POST'])
@limiter.limit('5 per hour')
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'All fields required'}), 400

        # Simple email regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
        if len(password) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400

        db = get_db()
        if db.users.find_one({'email': email}):
            return jsonify({'success': False, 'message': 'Email already exists'}), 409

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        db.users.insert_one({
            'name': name,
            'email': email,
            'password': hashed_password,
            'verified': False,
            'created_at': datetime.utcnow()
        })

        # Generate token
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt='email-verify')
        
        send_verification_email(email, token)

        return jsonify({'success': True, 'message': 'Registration successful. Please verify your email.'}), 201

    except Exception as e:
        logger.error(f"Register error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ===================== VERIFY =====================
@auth_bp.route('/auth/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-verify', max_age=86400)
    except SignatureExpired:
        return jsonify({'success': False, 'message': 'Verification link has expired.'}), 400
    except BadSignature:
        return jsonify({'success': False, 'message': 'Invalid verification link.'}), 400

    db = get_db()
    user = db.users.find_one({'email': email})
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404
        
    db.users.update_one({'email': email}, {'$set': {'verified': True}})
    
    return redirect('/login?verified=1')


# ===================== RESEND VERIFICATION =====================
@auth_bp.route('/auth/resend-verification', methods=['POST'])
@limiter.limit('3 per hour')
def resend_verification():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email required'}), 400
            
        db = get_db()
        user = db.users.find_one({'email': email})
        
        if user and not user.get('verified', False):
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(email, salt='email-verify')
            send_verification_email(email, token)
            
        return jsonify({'success': True, 'message': 'If the email is registered and unverified, a new link has been sent.'}), 200

    except Exception as e:
        logger.error(f"Resend verification error: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ===================== LOGOUT =====================
@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200


# ===================== AUTH CHECK =====================
@auth_bp.route('/auth/check', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'email': session.get('email'),
                'name': session.get('name')
            }
        })
    return jsonify({'authenticated': False})
