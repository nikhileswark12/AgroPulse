import re
import bcrypt
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app, redirect
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from pymongo.errors import DuplicateKeyError
from utils.logger import get_logger
from app import limiter, csrf
from utils.db_connection import get_db

auth_bp = Blueprint('auth', __name__)
logger = get_logger('auth')

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
            logger.info("Verification email sent")
        else:
            logger.warning("Verification email not sent because mail is not configured")
    except Exception as e:
        logger.error("Failed to send verification email: %s", e)

# ===================== LOGIN =====================
@auth_bp.route('/auth/login', methods=['POST'])
@csrf.exempt
@limiter.limit('10 per hour')
def login():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'A JSON object is required'}), 400
        email = data.get('email')
        if isinstance(email, str):
            email = email.strip().casefold()
        password = data.get('password')

        if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        if len(password.encode('utf-8')) > 72:
            return jsonify({'success': False, 'message': 'Password exceeds the allowed length'}), 400

        db = get_db()
        user = db.users.find_one({'email_normalized': email})

        if not user:
            logger.warning("Failed login attempt from ip=%s", request.remote_addr)
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        # Check password
        stored_hash = user['password']
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
            
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            logger.warning("Failed login attempt from ip=%s", request.remote_addr)
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        if not user.get('verified', False):
            logger.warning("Failed login attempt for unverified account from ip=%s", request.remote_addr)
            return jsonify({'success': False, 'message': 'Please verify your email before logging in'}), 401

        session.clear()
        session['user_id'] = str(user['_id'])
        session['email'] = user['email']
        session['name'] = user.get('name', '')
        session.permanent = True
        
        logger.info("Successful login from ip=%s", request.remote_addr)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': user['email'],
                'name': user.get('name', '')
            }
        }), 200

    except Exception as e:
        logger.error("Login error: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ===================== REGISTER =====================
@auth_bp.route('/auth/register', methods=['POST'])
@csrf.exempt
@limiter.limit('5 per hour')
def register():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'A JSON object is required'}), 400
        name = data.get('name')
        email = data.get('email')
        if isinstance(email, str):
            email = email.strip().casefold()
        password = data.get('password')

        if not isinstance(name, str) or not isinstance(email, str) or not isinstance(password, str) or not name.strip() or not email or not password:
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        name = name.strip()
        if len(name) > 120 or len(email) > 254 or len(password.encode('utf-8')) > 72:
            return jsonify({'success': False, 'message': 'Input exceeds the allowed length'}), 400

        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
        if len(password) < 8 or len(password.encode('utf-8')) > 72:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400

        db = get_db()
        if db.users.find_one({'email_normalized': email}):
            return jsonify({'success': False, 'message': 'Email already exists'}), 409

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        db.users.insert_one({
            'name': name,
            'email': email,
            'email_normalized': email,
            'password': hashed_password,
            'verified': False,
            'created_at': datetime.utcnow()
        })

        # Generate token
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt='email-verify')
        
        send_verification_email(email, token)
        
        logger.info("Successful account registration")

        return jsonify({'success': True, 'message': 'Registration successful. Please verify your email.'}), 201

    except Exception as e:
        if isinstance(e, DuplicateKeyError):
            return jsonify({'success': False, 'message': 'Email already exists'}), 409
        logger.error("Register error: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ===================== VERIFY =====================
@auth_bp.route('/auth/verify/<token>', methods=['GET'])
def verify_email(token):
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='email-verify', max_age=86400)
        if not isinstance(email, str):
            return jsonify({'success': False, 'message': 'Invalid verification link.'}), 400
        email = email.strip().casefold()
    except SignatureExpired:
        return jsonify({'success': False, 'message': 'Verification link has expired.'}), 400
    except BadSignature:
        return jsonify({'success': False, 'message': 'Invalid verification link.'}), 400

    db = get_db()
    user = db.users.find_one({'email_normalized': email})
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404
        
    db.users.update_one({'email_normalized': email}, {'$set': {'verified': True}})
    
    return redirect('/login?verified=1')


# ===================== RESEND VERIFICATION =====================
@auth_bp.route('/auth/resend-verification', methods=['POST'])
@csrf.exempt
@limiter.limit('3 per hour')
def resend_verification():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'A JSON object is required'}), 400
        email = data.get('email')
        if isinstance(email, str):
            email = email.strip().casefold()
        
        if not isinstance(email, str) or not email:
            return jsonify({'success': False, 'message': 'Email required'}), 400
            
        db = get_db()
        user = db.users.find_one({'email_normalized': email})
        
        if user and not user.get('verified', False):
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(email, salt='email-verify')
            send_verification_email(email, token)
            
        return jsonify({'success': True, 'message': 'If the email is registered and unverified, a new link has been sent.'}), 200

    except Exception as e:
        logger.error("Resend verification error: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ===================== LOGOUT =====================
@auth_bp.route('/auth/logout', methods=['POST'])
@csrf.exempt
def logout():
    session.clear()
    logger.info("Successful logout")
    return jsonify({'success': True, 'message': 'Logged out'}), 200


# ===================== FORGOT PASSWORD =====================
@auth_bp.route('/auth/forgot-password', methods=['POST'])
@csrf.exempt
@limiter.limit('3 per hour')
def forgot_password():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'A JSON object is required'}), 400
        email = data.get('email')
        if isinstance(email, str):
            email = email.strip().casefold()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email required'}), 400
            
        db = get_db()
        user = db.users.find_one({'email_normalized': email})
        
        response_msg = "If that email is registered you will receive a reset link"
        
        if user and user.get('verified', False):
            version = user.get('password_reset_version', 0)
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps({'email': email, 'version': version}, salt='password-reset')
            
            base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
            reset_link = f"{base_url}/password-reset/{token}"
            
            mail = current_app.config.get('MAIL')
            if mail:
                try:
                    msg = Message(
                        subject='Reset your AgroPulse password',
                        recipients=[email],
                        body=f'Please click the following link to reset your password: {reset_link}'
                    )
                    mail.send(msg)
                    logger.info("Password reset email sent")
                except Exception as e:
                    logger.error(f"Failed to send reset email: {e}")
                    logger.warning("Password reset email delivery failed")
            else:
                logger.warning("Password reset email not sent because mail is not configured")
                
        return jsonify({'success': True, 'message': response_msg}), 200
        
    except Exception as e:
        logger.error("Forgot password error: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ===================== RESET PASSWORD =====================
@auth_bp.route('/auth/reset-password', methods=['POST'])
@csrf.exempt
def reset_password():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'success': False, 'message': 'A JSON object is required'}), 400
        token = data.get('token')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not isinstance(token, str) or not isinstance(new_password, str) or not isinstance(confirm_password, str) or not token or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'All fields required'}), 400
            
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
            
        if len(new_password) < 8 or len(new_password.encode('utf-8')) > 72:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400
            
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            payload = serializer.loads(token, salt='password-reset', max_age=3600)
            if not isinstance(payload, dict):
                return jsonify({'success': False, 'message': 'Reset link has expired or already been used'}), 400
            email = payload.get('email')
            if not isinstance(email, str):
                return jsonify({'success': False, 'message': 'Reset link has expired or already been used'}), 400
            email = email.strip().casefold()
            token_version = payload.get('version', 0)
        except (SignatureExpired, BadSignature):
            logger.warning(f"Invalid or expired reset token submitted, ip={request.remote_addr}")
            return jsonify({'success': False, 'message': 'Reset link has expired or already been used'}), 400
            
        db = get_db()
        user = db.users.find_one({'email_normalized': email})
        
        if not user:
            return jsonify({'success': False, 'message': 'Reset link has expired or already been used'}), 400
            
        current_version = user.get('password_reset_version', 0)
        if token_version != current_version:
            logger.warning(f"Invalid or expired reset token submitted, ip={request.remote_addr}")
            return jsonify({'success': False, 'message': 'Reset link has expired or already been used'}), 400
            
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password': hashed_password,
                'password_reset_version': current_version + 1
            }}
        )
        
        logger.info("Password reset completed successfully")
        return jsonify({'success': True, 'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        logger.error("Reset password error: %s", e, exc_info=True)
        return jsonify({'success': False, 'message': 'Server error'}), 500


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
