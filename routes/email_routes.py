# This file contains the routes for sending password reset emails and resetting the password.
from flask import Blueprint, render_template, url_for, flash, redirect, session, current_app, request
from werkzeug.security import generate_password_hash
from db_initialize import db
from routes.user_routes import RequestResetForm, SetPasswordForm
from user_models import User
import smtplib
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer as Serializer

# Create a blueprint for the email routes
email_bp = Blueprint('email', __name__)

# Create a function to generate a token for the password reset
def generate_token(email):
    s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset-salt')
    return s.dumps(email, salt='password-reset')


# Create a function to verify the token for the password reset
def verify_token(token, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset-salt')
    try:
        email = s.loads(token, salt='password-reset', max_age=expiration)
    except Exception as e:
        print(f"Token verification error: {e}")
        return None
    return email

# Create a function to send the password reset email
def send_password_reset_email(user_email):
    print("Entering send_password_reset_email function...")

    # Send the email in a separate thread
    with current_app.app_context():
        try:
            print(f"Generating token for: {user_email}")
            token = generate_token(user_email)
            if not token:
                print("Failed to generate token.")
                return

            # Create the reset URL
            reset_url = url_for('email.reset_token', token=token, _external=True) # add this attrinute in production "_scheme='https'"
            print(f"Reset URL: {reset_url}")

            # Create the email message
            msg = EmailMessage()
            msg['Subject'] = 'Password Reset Request'
            msg['From'] = current_app.config['MAIL_USERNAME']
            msg['To'] = user_email
            msg_content = f"""
            <html>
                <body>
                    <p>Hello,</p>
                    <p>To reset your password, please click on the link below:</p>
                    <a href="{reset_url}">Reset Password</a>
                    <p>If you did not request a password reset, please ignore this email and your password will remain unchanged.</p>
                </body>
            </html>
            """

            # Add the HTML content to the email message
            msg.add_alternative(msg_content, subtype='html')
            print("HTML email message created.")

            # Send the email
            print(f"Connecting to SMTP server: {current_app.config['MAIL_SERVER']}")
            with smtplib.SMTP_SSL(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as smtp:
                print("SMTP connection established.")
                print("Logging in to SMTP server...")
                smtp.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
                print("Logged in successfully.")
                print("Sending email...")
                smtp.send_message(msg)
                print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")


# Create a route for the password reset request
@email_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if 'user_id' in session:
        return redirect(url_for('index'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # Send the password reset email if the user is found
        if user:
            send_password_reset_email(user.email)
            flash('An email has been sent with instructions to reset your password.', 'info')

        # Flash message when the user is not found, i.e., a specific condition after the form submission
        else:
            flash('No account found with that email address.', 'warning')

        # Redirect after flashing the message, regardless of whether the user was found
        return redirect(url_for('user.login'))

    # Render the reset request form
    return render_template('reset_request.html', title='Reset Password', form=form)


# Create a route for the password reset and include the token in the URL
@email_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # Redirect the user to the index if they are already logged in
    if 'user_id' in session:
        print("User already logged in, redirecting to index.")
        return redirect(url_for('index'))

    # Verify the token

    # Redirect the user to the reset request form if the token is invalid or expired
    if (user_email := verify_token(token)) is None:
        flash('That is an invalid or expired token', 'warning')
        print("Invalid or expired token.")
        return redirect(url_for('email.reset_request'))

    # Create a form for the password reset
    form = SetPasswordForm()

    # Update the user's password if the form is submitted and valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=user_email).first()

        # Update the user's password and commit the changes to the database
        if user:
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            print(f"Password for {user.email} has been updated.")
            flash('Your password has been updated! You are now able to log in.', 'success')
            return redirect(url_for('user.login'))

        # Flash a message if the user is not found
        else:
            print(f"User not found for email {user_email}")

    return render_template('reset_token.html', title='Reset Password', form=form)


