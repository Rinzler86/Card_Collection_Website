# This file contains the forms for the user authentication and account management
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Optional


# Create a login form that inherits from FlaskForm and contains email, password, and submit fields from wtforms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Create a signup form that inherits from FlaskForm and contains email, username, first_name, last_name, password, and confirm fields from wtforms
class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Sign Up')


# Create a form for updating the user account that inherits from FlaskForm and contains first_name, last_name, and submit fields from wtforms
class AccountUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[Optional()])
    last_name = StringField('Last Name', validators=[Optional()])
    submit = SubmitField('Update')


# Create a form for requesting a password reset that inherits from FlaskForm and contains email and submit fields from wtforms
class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
                             DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Reset Password')

