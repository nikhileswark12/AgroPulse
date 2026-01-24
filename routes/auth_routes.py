from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def get_db():
    return current_app.config['MONGO_DB']

# ===================== LOGIN =====================
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400

        db = get_db()
        user = db.users.find_one({'email': email})

        if not user or not check_password_hash(user['password'], password):
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

        session['user_id'] = str(user['_id'])
        session['email'] = user['email']
        session['name'] = user.get('name', '')

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
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'All fields required'}), 400

        db = get_db()
        if db.users.find_one({'email': email}):
            return jsonify({'success': False, 'message': 'Email already exists'}), 409

        db.users.insert_one({
            'name': name,
            'email': email,
            'password': generate_password_hash(password)
        })

        return jsonify({'success': True, 'message': 'Registration successful'}), 201

    except Exception as e:
        logger.error(f"Register error: {e}", exc_info=True)
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
