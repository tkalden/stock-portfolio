import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from utilities.model import User
from utilities.userFunction import UserCRUD

auth = Blueprint('auth', __name__)
UserCRUD = UserCRUD()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def validate_name(name):
    """Validate name format"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    if not re.match(r'^[a-zA-Z\s]+$', name.strip()):
        return False, "Name can only contain letters and spaces"
    return True, "Name is valid"

@auth.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'message': 'Already logged in',
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            }
        })
    
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    # Validate input
    if not email or not password:
        return jsonify({'success': False, 'error': 'Please provide both email and password'}), 400
    
    if not validate_email(email):
        return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
    
    try:
        # Get user from database
        user = User.get(email)
        
        if not user:
            return jsonify({'success': False, 'error': 'Email not found. Please sign up first!'}), 404
        
        # Check password
        if not check_password_hash(user.password, password):
            return jsonify({'success': False, 'error': 'Invalid password. Please check your credentials and try again.'}), 401
        
        # Login successful
        login_user(user, remember=remember)
        return jsonify({
            'success': True,
            'message': f'Welcome back, {user.name}!',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'An error occurred during login. Please try again.'}), 500

@auth.route('/api/signup', methods=['POST'])
def api_signup():
    """API endpoint for user signup"""
    if current_user.is_authenticated:
        return jsonify({
            'success': True,
            'message': 'Already logged in',
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email
            }
        })
    
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    password = data.get('password', '')
    confirm = data.get('confirm', '')
    
    # Validate input
    if not all([email, name, password, confirm]):
        return jsonify({'success': False, 'error': 'Please fill in all fields'}), 400
    
    # Validate email
    if not validate_email(email):
        return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
    
    # Validate name
    name_valid, name_message = validate_name(name)
    if not name_valid:
        return jsonify({'success': False, 'error': name_message}), 400
    
    # Validate password
    password_valid, password_message = validate_password(password)
    if not password_valid:
        return jsonify({'success': False, 'error': password_message}), 400
    
    # Check password confirmation
    if password != confirm:
        return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
    
    try:
        # Check if user already exists
        existing_user = User.get(email)
        if existing_user:
            return jsonify({'success': False, 'error': 'Email address already exists. Please try logging in'}), 409
        
        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        success = UserCRUD.save_user_data(email=email, name=name, password=hashed_password)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please log in with your credentials.'
            })
        else:
            return jsonify({'success': False, 'error': 'Registration failed. Please try again.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': 'An error occurred during registration. Please try again.'}), 500

@auth.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for user logout"""
    logout_user()
    return jsonify({
        'success': True,
        'message': 'You have been successfully logged out. Thanks for visiting Stocknity!'
    })

@auth.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    """API endpoint for newsletter subscription"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    subscribe_email = data.get('email', '').strip().lower()
    
    if not subscribe_email:
        return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
    
    if not validate_email(subscribe_email):
        return jsonify({'success': False, 'error': 'Please enter a valid email address'}), 400
    
    try:
        UserCRUD.subscribe(subscribe_email)
        return jsonify({
            'success': True,
            'message': 'Thank you for subscribing to our newsletter!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': 'Subscription failed. Please try again.'}), 500

# Legacy routes for backward compatibility (redirect to React frontend)
@auth.route('/login', methods=['GET', 'POST'])
def login():
    return jsonify({'error': 'Please use the React frontend for login'}), 400

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    return jsonify({'error': 'Please use the React frontend for signup'}), 400

@auth.route('/logout')
def logout():
    return jsonify({'error': 'Please use the React frontend for logout'}), 400

@auth.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    return jsonify({'error': 'Please use the React frontend for subscription'}), 400 



