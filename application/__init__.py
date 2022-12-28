from .models import User
from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      app.logger.info("Currently no production config is setup.")
      raise Exception("Currently no production config is setup.")
    else:
      app.logger.info("Staring Local Development.")
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please login first'
     
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    app.app_context().push()
    app.logger.info("App setup complete")
    return app