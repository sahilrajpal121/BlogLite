from .database import db
import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # doj = db.Column(db.DateTime(), default=datetime.datetime.now, nullable=False)
    # profile_pic = db.Column(db.String(120), default='default_profile_pic.png', nullable=False)
    # bio = db.Column(db.String(), nullable=True)
    posts = db.relationship('Post', backref='user', lazy=True, cascade="all, delete")


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
