from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configure CORS for React frontend (stocknity-ui)
    CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['REDIS_HOST'] = os.environ.get('REDIS_HOST', 'localhost')
    app.config['REDIS_PORT'] = int(os.environ.get('REDIS_PORT', 6379))
    app.config['REDIS_DB'] = int(os.environ.get('REDIS_DB', 0))
    
    # Initialize extensions
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from utilities.model import User
        return User.get(user_id)
    
    # Import and register blueprints
    from auth import auth
    app.register_blueprint(auth)
    
    from main import main
    app.register_blueprint(main)
    
    # Start the data scheduler
    from scheduler import data_scheduler
    data_scheduler.start_scheduler()
    
    return app