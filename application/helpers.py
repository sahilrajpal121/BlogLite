from email_validator import validate_email, EmailNotValidError
from flask import flash
import re

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