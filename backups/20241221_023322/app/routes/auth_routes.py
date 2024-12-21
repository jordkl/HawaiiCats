from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, current_app
import firebase_admin
from firebase_admin import auth, credentials
from functools import wraps
from ..auth import login_required

bp = Blueprint('auth', __name__)

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
            session['id_token'] = token  # Store the ID token in session
            
            return jsonify({'success': True, 'redirect': url_for('auth.dashboard')})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    # GET request - show the login form with Firebase config
    return render_template('login.html', config={
        'FIREBASE_API_KEY': current_app.config['FIREBASE_API_KEY'],
        'FIREBASE_PROJECT_ID': current_app.config['FIREBASE_PROJECT_ID'],
        'FIREBASE_AUTH_DOMAIN': current_app.config['FIREBASE_AUTH_DOMAIN'],
        'FIREBASE_STORAGE_BUCKET': current_app.config['FIREBASE_STORAGE_BUCKET'],
        'FIREBASE_MESSAGING_SENDER_ID': current_app.config['FIREBASE_MESSAGING_SENDER_ID']
    })

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