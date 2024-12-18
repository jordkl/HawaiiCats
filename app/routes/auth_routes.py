from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
import firebase_admin
from firebase_admin import auth, credentials
from functools import wraps

bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415
            
        try:
            # Get the ID token from the request
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return jsonify({'error': 'No token provided'}), 400

            # Verify the Firebase ID token
            decoded_token = auth.verify_id_token(token)
            user_id = decoded_token['uid']
            
            # Set session data
            session['user_id'] = user_id
            session['email'] = decoded_token.get('email', '')
            
            return jsonify({'success': True, 'redirect': url_for('auth.dashboard')})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    # GET request - show the login form
    return render_template('login.html')

@bp.route('/admin')
@login_required
def admin():
    """Protected dashboard page"""
    return render_template('admin.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard page"""
    return render_template('dashboard.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))