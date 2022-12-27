from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from application.models import User, Post, Comment, Like, Follower
from email_validator import validate_email
from .helpers import wrong_email_input, invalid_username
from .database import db

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').lower()
        email = request.form.get('email').lower()
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        
        user = User.query.filter_by(username=username).first()
        
        if invalid_username(username):
            flash('Username is not valid', category='error')
        elif user:
            flash('Username already exists', category='error')
        elif wrong_email_input(email):
            flash('Email is not valid', category='error')
        elif password != password_confirm:
            flash('Passwords do not match', category='error')
        
        new_user = User(
            username=username, 
            email=email, 
            password=generate_password_hash(password, method='sha256')
            )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email').lower()
        password = request.form.get('password')
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

    return render_template('login.html')
        

