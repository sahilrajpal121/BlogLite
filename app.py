from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from application.config import LocalDevelopmentConfig
# from flask_security import Security, UserMixin, RoleMixin
import datetime
# from flask_security import SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
# from flask_security.utils import hash_password
# from flask_security.forms import ConfirmRegisterForm
# from wtforms import StringField
# from wtforms.validators import DataRequired
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


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
    app.app_context().push()
    app.logger.info("App setup complete")
    return app

app = create_app()

db = SQLAlchemy(app)
db.init_app(app)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)
    # doj = db.Column(db.DateTime(), default=datetime.datetime.now, nullable=False)
    # profile_pic = db.Column(db.String(120), default='default_profile_pic.png', nullable=False)
    # bio = db.Column(db.String(), nullable=True)

    roles = db.relationship('Role', secondary='roles_users',
                             backref=db.backref('users', lazy='dynamic'))
    posts = db.relationship('Post', backref='user', lazy=True, cascade="all, delete")


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Post(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    # content = db.Column(db.String(), nullable=False)
    date_posted = db.Column(db.DateTime(), default=datetime.datetime.now, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # caption = db.Column(db.String(120), nullable=True)
    # image = db.Column(db.String(120), nullable=True)
    # is_archived = db.Column(db.Boolean(), default=False, nullable=False)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='delete')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='delete')

class Follower(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.String(), nullable=False)
    date_posted = db.Column(db.DateTime(), default=datetime.datetime.now, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

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

class ExtendRegistrationForm(ConfirmRegisterForm):
    username = StringField('username', [DataRequired()])

if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore,
                        register_form=ExtendRegistrationForm)

    # create_test(user_datastore)
    app.run(host='0.0.0.0',port=8080, debug=True)
    
    