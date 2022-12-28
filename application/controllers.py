from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from application.models import User, Post, Comment, Like, Follower
from email_validator import validate_email
from .helpers import wrong_email_input, invalid_username
from .database import db
from .forms import RegisterForm, LoginForm

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':

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
    if current_user.is_authenticated:
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