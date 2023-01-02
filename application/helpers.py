from email_validator import validate_email, EmailNotValidError
from flask import flash
import re
from PIL import Image, ImageOps
from flask_login import current_user
from .models import IST
from datetime import datetime

def wrong_email_input(email):
    try:
        validate_email(email)
    except EmailNotValidError as e:
        flash(e)
        return True
    
def invalid_username(username):
    username_valid = re.match('^[a-zA-Z_\d\.]+$', username)
    
    if username_valid is None:
        return True
    return False

def resize_image(image, size):
    image = Image.open(image)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    return image

def title_exists(title):
    for post in current_user.posts:
        if post.title == title:
            return True
    return False

def get_time():
    return datetime.now(IST)