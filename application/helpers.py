import re
from PIL import Image, ImageOps
from flask_login import current_user
from .models import IST
from datetime import datetime
import os
from flask import current_app as app
    
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

def rename_and_save_post_image(image, title):
    image_ext = image.filename.split('.')[-1]
    image_name = f'{current_user.id}_{title}.{image_ext}'
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'posts/{image_name}')
    image.save(image_path)
    return image_name
