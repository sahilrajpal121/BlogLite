from .database import db
import datetime
from flask_login import UserMixin
import pytz
IST = pytz.timezone('Asia/Kolkata')


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('following_id', db.Integer, db.ForeignKey('user.id'))
)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(120), default='default_profile_picture.png', nullable=False)
    posts = db.relationship('Post', backref='user', lazy='dynamic', cascade="all, delete")
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade="all, delete")
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade="all, delete")

    # self referential many to many relationship for followers
    following = db.relationship('User', secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.following_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def __repr__(self) -> str:
        return f'<User: {self.username}>'

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)
        else:
            print('You are already following this user')

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
        else:
            print('You are not following this user')

    def is_following(self, user):
        return self.following.filter(
            followers.c.following_id == user.id).count() > 0

    def is_liked(self, post):
        return post.likes.filter_by(user_id=self.id).count() > 0


class Post(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    date_posted = db.Column(db.DateTime(), default=datetime.datetime.now(IST), nullable=False)
    author_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    image = db.Column(db.String(120), nullable=True)
    is_archived = db.Column(db.Boolean(), default=False, nullable=False)
    date_edited = db.Column(db.DateTime(), nullable=True)

    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='delete')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='delete')

    def __repr__(self) -> str:
        return f'<Post: {self.title}>'
    
    def last_action(self):
        if self.date_edited:
            return 'Edited ' + self.date_edited.strftime('%I:%M %p - %b %d, %Y')
        else:
            return 'Created ' + self.date_posted.strftime('%I:%M %p - %b %d, %Y')

class Comment(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.String(), nullable=False)
    date_posted = db.Column(db.DateTime(), default=datetime.datetime.now(IST), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)