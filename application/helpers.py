from email_validator import validate_email, EmailNotValidError
from flask import flash
import re
from PIL import Image, ImageOps

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