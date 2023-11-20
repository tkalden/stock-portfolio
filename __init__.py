from flask import Flask
from flask_login import LoginManager
from flask_toastr import Toastr

from methods.redis import redis_cache
from utilities.model import User


def create_app():
    app = Flask(__name__)
    app.deug = True
    app.config['REDIS_URL'] = "redis://localhost:6379/0"
    redis_cache.init_app(app)

    toastr = Toastr()

    config = {
        "SECRET_KEY": "e0af172472bfdc4bc8292763f86e3abe0e2eb9a8cf68d12f"
    }

    app = Flask(__name__)
    app.config.from_mapping(config)
    toastr.init_app(app)

      # The login manager contains the code that lets your application and Flask-Login work together
    login_manager = LoginManager() # Create a Login Manager instance
    login_manager.login_view = 'auth.login' # define the redirection path when login required and we attempt to access without being logged in
    login_manager.init_app(app) # configure it for login


    @login_manager.user_loader
    def load_user(user_id): #reload user object from the user ID stored in the session
        user = User.get(user_id)
        print('User', user)
        return user

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app