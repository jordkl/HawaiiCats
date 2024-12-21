from flask import Blueprint, render_template, current_app

bp = Blueprint('main', __name__, template_folder='templates')

@bp.route('/')
def index():
    """Render the index page"""
    return render_template('index.html')

@bp.route('/calculator')
def calculator():
    """Render the calculator page"""
    return render_template('calculator.html')

@bp.route('/catmap')
def catmap():
    """Render the catmap page"""
    return render_template('catmap.html')

@bp.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    return render_template('dashboard.html')

@bp.route('/mobile-app')
def mobile_app():
    """Render the mobile app page"""
    return render_template('mobile_app.html', 
                         recaptcha_site_key=current_app.config['RECAPTCHA_SITE_KEY'])
