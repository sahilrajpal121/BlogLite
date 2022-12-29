from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileAllowed, FileField
from flask_wtf import FlaskForm
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Comment')