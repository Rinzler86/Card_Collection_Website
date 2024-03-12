# This file contains the routes for user authentication and account management
import os
import secrets
from PIL import Image
from flask import flash, redirect, url_for, render_template, session, Blueprint, current_app, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from forms import LoginForm, SignupForm, AccountUpdateForm, PasswordResetForm
from user_models import User
from db_initialize import db

user_bp = Blueprint('user', __name__)

# Create a route to log in the user
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['first_name'] = user.first_name
            flash('You were successfully logged in', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)


# Create a route to log out the user
@user_bp.route('/logout')
def logout():
    session.clear()  # Clears the entire session
    flash('You were logged out', 'success')
    return redirect(url_for('index'))


# Create a route to sign up a new user
@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user_exists = User.query.filter_by(email=form.email.data).first()
        if user_exists:
            flash('Email already registered', 'warning')
            return render_template('signup.html', form=form)
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, username=form.username.data,
                        first_name=form.first_name.data, last_name=form.last_name.data,
                        password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('user.login'))
    return render_template('signup.html', form=form)


# Create a route to view the user's account details and update them
@user_bp.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'info')
        return redirect(url_for('user.login'))

    user = User.query.get(session['user_id'])
    print(f"Loaded user: {user.username}")

    update_form = AccountUpdateForm(obj=user)  # Pre-populate form
    password_form = PasswordResetForm()
    profile_form = UpdateProfileForm()

    if 'update_account' in request.form:
        print("Update account form submitted")
        if update_form.validate_on_submit():
            print("Update account form validated")
            user.first_name = update_form.first_name.data
            user.last_name = update_form.last_name.data
            db.session.commit()
            session['user_name'] = user.username
            session['first_name'] = user.first_name
            flash('Your account details have been updated.', 'success')
            return redirect(url_for('user.account'))
        else:
            print("Update account form validation failed")

    if 'update_profile_picture' in request.form:
        print("Update profile picture form submitted")
        if profile_form.validate_on_submit():
            print("Profile picture form validated")
            if profile_form.picture.data:
                picture_file = save_picture(profile_form.picture.data)
                user.user_image = picture_file
                db.session.commit()
                flash('Your profile picture has been updated.', 'success')
                return redirect(url_for('user.account'))
            else:
                print("No picture data found")
        else:
            print("Profile picture form validation failed")

    image_file = url_for('static', filename='user_profile_pics/' + user.user_image if user.user_image else 'default.jpg')
    return render_template('account.html', title='Account',
                           update_form=update_form,
                           password_form=password_form,
                           profile_form=profile_form,
                           image_file=image_file)


# Create a route to reset the user's password
@user_bp.route('/reset_password', methods=['POST'])
def reset_password():
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.get(session['user_id'])
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('user.account'))

    return render_template('account.html', update_form=AccountUpdateForm(), password_form=form)


# Create a route to delete the user's account
@user_bp.route('/delete_account', methods=['POST'])
def delete_account():
    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id', None)
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('index'))


# create a route to view the user's profile
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    # Custom validation to check if the email exists in the database
    def validate_email(self, email):
        if (user := User.query.filter_by(email=email.data.lower()).first()) is None:
            raise ValidationError('There is no account with that email. You must register first.')

# create a set a new password form
class SetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm New Password')
    submit = SubmitField('Set New Password')

# create a form to update the user's profile picture
class UpdateProfileForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')


# create a function to save the user's profile picture
def save_picture(form_picture):
    print("Entering save_picture function")

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/user_profile_pics', picture_fn)

    print(f"File name after processing: {picture_fn}")
    print(f"Path for saving picture: {picture_path}")

    # Resize image
    output_size = (125, 125)
    try:
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
        print("Picture saved successfully")
    except Exception as e:
        print(f"Error resizing/saving image: {e}")

    # Return the file name to be stored in the database
    return picture_fn

