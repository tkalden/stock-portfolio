from flask import Flask, request, jsonify
from flask_login import LoginManager
from flask_cors import CORS
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
import logging

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Security Configuration
    configure_security(app)
    
    # Configure CORS with environment-based origins
    configure_cors(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        # Generate a secure key if not provided
        app.config['SECRET_KEY'] = secrets.token_hex(32)
        logging.warning("SECRET_KEY not set - generated temporary key. Set SECRET_KEY environment variable for production.")
    
    app.config['REDIS_HOST'] = os.environ.get('REDIS_HOST', 'localhost')
    app.config['REDIS_PORT'] = int(os.environ.get('REDIS_PORT', 6379))
    app.config['REDIS_DB'] = int(os.getenv('REDIS_DB', 0))
    
    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from utilities.model import User
        return User.get(user_id)
    
    # Security middleware
    setup_security_middleware(app)
    
    # Import and register blueprints
    from src.api.auth import auth
    app.register_blueprint(auth)
    
    from src.api.main import main
    app.register_blueprint(main)
    
    # Note: Async scheduler is started via API endpoints
    # Use /api/scheduler/start to start the background scheduler
    # Old scheduler has been replaced with async_scheduler
    
    return app

def configure_security(app):
    """Configure security settings"""
    # Production security settings
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # Security headers
    if os.environ.get('ENABLE_SECURITY_HEADERS', 'true').lower() == 'true':
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Content Security Policy
            csp_parts = []
            default_src = os.environ.get('CSP_DEFAULT_SRC', "'self'")
            script_src = os.environ.get('CSP_SCRIPT_SRC', "'self' 'unsafe-inline'")
            style_src = os.environ.get('CSP_STYLE_SRC', "'self' 'unsafe-inline'")
            img_src = os.environ.get('CSP_IMG_SRC', "'self' data: https:")
            connect_src = os.environ.get('CSP_CONNECT_SRC', "'self' https:")
            
            csp_parts.append(f"default-src {default_src}")
            csp_parts.append(f"script-src {script_src}")
            csp_parts.append(f"style-src {style_src}")
            csp_parts.append(f"img-src {img_src}")
            csp_parts.append(f"connect-src {connect_src}")
            
            response.headers['Content-Security-Policy'] = '; '.join(csp_parts)
            return response

def configure_cors(app):
    """Configure CORS with environment-based origins"""
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001')
    origins = [origin.strip() for origin in allowed_origins.split(',')]
    
    CORS(app, origins=origins, supports_credentials=True)

def setup_security_middleware(app):
    """Setup security middleware"""
    # Rate limiting
    from collections import defaultdict
    import time
    
    request_counts = defaultdict(list)
    
    def rate_limit(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Clean old requests
            request_counts[client_ip] = [req_time for req_time in request_counts[client_ip] 
                                       if current_time - req_time < 60]
            
            # Check rate limits
            requests_per_minute = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', 100))
            requests_per_hour = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_HOUR', 1000))
            
            if len(request_counts[client_ip]) >= requests_per_minute:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Add current request
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    
    # Apply rate limiting to all API routes
    for endpoint in app.view_functions:
        if endpoint.startswith('api.'):
            app.view_functions[endpoint] = rate_limit(app.view_functions[endpoint])