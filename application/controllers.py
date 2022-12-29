from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from application.models import User, Post, Comment, Like, Follower
from email_validator import validate_email
from .helpers import wrong_email_input, invalid_username
from .database import db
from .forms import RegisterForm, LoginForm, PostForm, CommentForm
import logging


@app.route('/')
@login_required
def index():
    # app.logger.debug('Index page accessed')
    print('index page accessed')
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in! Please log out to register', 'info')
        return redirect(url_for('login'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        email = form.email.data.lower()
        password = form.password.data
        password_confirm = form.confirm_password.data

        username_exist = User.query.filter_by(username=username).first()
        email_exist = User.query.filter_by(email=email).first()
        
        if invalid_username(username):
            flash('Username is not valid', category='warning')
        elif username_exist:
            flash('Username already exists', category='warning')
        elif email_exist:
            flash('Email already exists', category='warning')
        # elif wrong_email_input(email):
        #     pass
        elif password != password_confirm:
            flash('Passwords do not match', category='warning')
        else:
            new_user = User(
                username=username, 
                email=email, 
                password=generate_password_hash(password, method='sha256')
                )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created. Please log in.', category='success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info('Login page accessed')
    app.logger.debug('login page debug')
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('index'))
    form = LoginForm()
     
    if request.method == 'POST':
        username_or_email = form.username_or_email.data
        password = form.password.data
        user = User.query.filter(
            (User.username==username_or_email) |\
            (User.email==username_or_email)
            ).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('logged in successful', category='success')
                return redirect(url_for('index'))
            else:
                flash('Wrong password', category='warning')
        else:
            flash("Username or email doesn't exist", category='warning')

    return render_template('login.html', form=form)
        

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/create_blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    print('Create blog page accessed')

    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        image = form.image.data
        print(image.filename)
        new_post = Post(title=title, content=content, author_id=current_user.id, image=image.filename)
        db.session.add(new_post)
        db.session.commit()
        flash('Blog created', category='success')
        return redirect(url_for('index'))

    return render_template('create_blog.html', form=form)


@app.route("/profile/<string:username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        posts = Post.query.filter_by(author_id=user.id).all()
        followed = Follower.query.filter_by(follower_id=current_user.id, following_id=user.id).first()
        no_followers = Follower.query.filter_by(following_id=user.id).count()
        no_following = Follower.query.filter_by(follower_id=user.id).count()
        return render_template('profile.html', user=user, posts=posts, no_followers=no_followers, no_following=no_following, followed=followed)
