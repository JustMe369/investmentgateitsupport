from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators

class LoginForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(message='Username is required'),
        validators.Length(min=3, max=50, message='Username must be between 3 and 50 characters')
    ])
    password = PasswordField('Password', [
        validators.DataRequired(message='Password is required'),
        validators.Length(min=6, message='Password must be at least 6 characters')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
