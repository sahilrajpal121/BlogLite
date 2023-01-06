from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from application.models import User, Post, Comment, Like
from email_validator import validate_email
from .helpers import wrong_email_input, invalid_username, title_exists, resize_image, get_time
from .database import db
from .forms import RegisterForm, LoginForm, PostForm, CommentForm, EditProfileForm, SearchForm
import logging
from .config import LocalDevelopmentConfig
import os
from PIL import Image, ImageOps
from urllib.parse import quote, unquote

@app.route('/')
@login_required
def index():
    print('index page accessed')
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    filtered_posts = []
    following_ids = [user.id for user in current_user.following]
    print(following_ids)
    for post in posts:
        if post.author_id in following_ids:
            filtered_posts.append(post)
    return render_template('index.html', posts=filtered_posts, quote_func=quote)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in! Please log out to register', 'info')
        return redirect(url_for('index'))
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
        if title_exists(form.title.data):
            flash('Title already exists', category='warning')
            return redirect(url_for('create_blog'))
        title = form.title.data
        content = form.content.data
        content = content.replace('\n', '<br>')
        image = form.image.data
        new_post = Post(title=title, content=content, author_id=current_user.id)
        if image:
            image_ext = image.filename.split('.')[-1]
            image_name = f'{current_user.id}_{title}.{image_ext}'
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'posts/{image_name}')
            image.save(image_path)
            new_post.image = image_name

        db.session.add(new_post)
        db.session.commit()
        flash('Blog created', category='success')
        return redirect(url_for('post', post_title=quote(title), username=current_user.username))

    return render_template('create_blog.html', form=form)


@app.route("/profile/<string:username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        posts = user.posts.order_by(Post.date_posted.desc()).all()
        followed = current_user.is_following(user)
        no_followers = user.followers.count()
        no_following = user.following.count()
        return render_template('profile.html', user=user, posts=posts, no_followers=no_followers, no_following=no_following, followed=followed, quote_func=quote)
    else:
        abort(404, description='User not found')


@app.route('/follow/<string:username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user:
        followed = current_user.is_following(user)
        if user == current_user:
            abort(405, description='You cannot follow yourself')
        elif not followed:
            current_user.follow(user)
            db.session.commit()
            flash('You are now following '+username, category='success')

        return redirect(request.referrer)
    else:
        abort(404, description='User not found')


@app.route('/unfollow/<string:username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user:

        followed = current_user.is_following(user)
        if followed:
            current_user.unfollow(user)
            db.session.commit()
            flash(f'You are no longer following <strong>{username}</strong>', category='success')
        return redirect(request.referrer)
    else:
        abort(404, description='User not found')

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():

        username = form.username.data
        email = form.email.data
        image = form.image.data
        username_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        if (username != current_user.username) and username_exists:
            app.logger.debug(f'{username_exists} and {current_user.username}')
            flash('Username already exists, Try another one', category='warning')
        elif (email != current_user.email) and email_exists:
            flash('Email already exists, Try another one', category='warning')
        else:
            current_user.username = username
            current_user.email = email
            if image:
                image_extension = image.filename.split('.')[-1]
                image_pil = Image.open(image)
                image_resized = ImageOps.contain(image_pil, (720, 960))
                current_user.profile_pic = f'{current_user.id}.{image_extension}'
                image_resized.save(os.path.join(app.config['UPLOAD_FOLDER'], f'profile_pictures/{current_user.profile_pic}'))
                
            db.session.commit()
            flash('Profile updated', category='success')
            return redirect(url_for('profile', username=current_user.username))


    return render_template('edit_profile.html', form=form)


@app.route('/profile/<string:username>/followers')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user:
        users = user.followers.all()
        return render_template('follow.html', user=user, users=users)
    else:
        abort(404, description='User not found')

@app.route('/profile/<string:username>/following')
@login_required
def following(username):
    user = User.query.filter_by(username=username).first()
    if user:
        users = user.following.all()
        return render_template('follow.html', user=user, users=users)
    else:
        abort(404, description='User not found')
    

@app.route('/post/<string:username>/<string:post_title>/')
@login_required
def post(username, post_title):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404, description='User not found')
    
    post_title = unquote(post_title)
    post = Post.query.filter_by(title=post_title, author_id=user.id).first()
    if post:
        comments = post.comments.order_by(Comment.date_posted.desc()).all()
        return render_template('post.html', post=post, quote_func=quote, comments=comments)
    else:
        abort(404, description='Post not found')


@app.route('/post/<string:username>/<string:post_title>/like')
@login_required
def like_toggle(username, post_title):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        abort(404, description='User not found')
    
    post_title = unquote(post_title)
    post = Post.query.filter_by(title=post_title, author_id=user.id).first()
    
    if not post:
        abort(404, description='Post not found')
        
    already_liked = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if already_liked:
        db.session.delete(already_liked)
        db.session.commit()
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        db.session.commit()
    return redirect(request.referrer)

@app.route('/post/<string:post_title>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_title):
    post_title = unquote(post_title)
    post = Post.query.filter_by(title=post_title, author_id=current_user.id).first()
    if post:
        form = PostForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            title_exists = Post.query.filter_by(title=title, author_id=current_user.id).first()
            if (post.title != title) and title_exists:
                flash('Title already exists, Try another one', category='warning')
            else:
                post.title = title
                post.content = content
                post.date_edited = get_time()
                if form.image.data:
                    image = form.image.data
                    image_extension = image.filename.split('.')[-1]
                    image_pil = Image.open(image)
                    image_resized = ImageOps.contain(image_pil, (720, 960))
                    post.image = f'{post.id}.{image_extension}'
                    image_resized.save(os.path.join(app.config['UPLOAD_FOLDER'], f'post_pictures/{post.image}'))
                db.session.commit()
                flash('Post updated', category='success')
                return redirect(url_for('post', username=current_user.username, post_title=quote(post.title)))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
    else:
        abort(404, description='Post not found')
    return render_template('edit_post.html', form=form, post=post, quote_func=quote)

@app.context_processor
def base_comment():
    form = CommentForm()
    return dict(form=form)

@app.route('/post/<string:username>/<string:post_title>/comment', methods=['POST'])
@login_required
def comment(username, post_title):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404, description='User not found')
    
    post_title = unquote(post_title)
    post = Post.query.filter_by(title=post_title, author_id=user.id).first()
    
    if not post:
        abort(404, description='Post not found')
    
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(content=form.comment.data, author_id=current_user.id, post_id=post.id, date_posted=get_time())
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added', category='success')
    else:
        flash('Comment field is empty', category='warning')
    return redirect(url_for('post', username=user.username, post_title=quote(post.title)))

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search_query = form.searching.data
        users = User.query.filter(User.username.contains(search_query)).all()
        return render_template('search_results.html', search_query=search_query, form=form, users=users)
    else:
        # flash('Search field is empty', category='warning')
        # return redirect(url_for('index'))
        return render_template('invalid_search.html')

@app.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted', category='success')
        return redirect(request.referrer)
    else:
        abort(404, description='Comment not found')
    

@app.route('/post/<string:post_title>/delete_post')
@login_required
def delete_post(post_title):
    post_title = unquote(post_title)
    post = Post.query.filter_by(title=post_title, author_id=current_user.id).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category='success')
        return redirect(url_for('profile', username=current_user.username))
    else:
        abort(404, description='Post not found')
    
@app.route('/delete_account')
@login_required
def delete_account():
    user = User.query.filter_by(id=current_user.id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Account deleted', category='success')
        return redirect(url_for('register'))
    else:
        abort(404, description='User not found')
