from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_login import LoginManager
import os


app = None

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
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    app.app_context().push()
    app.logger.info("App setup complete")
    return app

app = create_app()


def create_test(user_datastore):
    user_datastore.create_user(username='user1', password='password1', email='user1@mail.com')
    user2 = User(username='user2', password='password2', email='user2@mail.com')
    # user3 = User(username='user3')
    # user4 = User(username='user4')
    post1 = Post(title='post1', author_id=1)
    post2 = Post(title='post2', author_id=2)
    # Posts = Posts(title='post3', author_id=3)
    # Posts = Posts(title='post4', author_id=4)
    comment1 = Comment(content='comment1', post_id=1, author_id=1)
    comment2 = Comment(content='comment2', post_id=2, author_id=2)
    db.session.add_all([user2, post1, post2, comment1, comment2])
    db.session.commit()

from application.controllers import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
    