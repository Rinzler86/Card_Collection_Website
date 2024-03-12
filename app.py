# Description: This is the main file for the Flask app. It initializes the app and the database, and registers the blueprints.
from datetime import datetime
from flask import Flask, render_template, request, session, url_for
from db_initialize import csrf, db
from flask_mail import Mail
from routes.merchant_routes import merchant_bp
from ignore_creds import PASSWORD, SECRET_KEY, FLASK_MAIL_KEY, FLASK_MAIL_EMAIL, FLASK_EMAIL_PASSWORD

# Initialize Flask-Mail
mail = Mail()

# Create the Flask app
def create_app():
    """
    Factory function to create and configure a Flask application object.

    Returns:
        app (Flask): The configured Flask application object.
    """
    # Initialize the app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = f'{SECRET_KEY}'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://pokeuser:{PASSWORD}@localhost/pokemon_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with the app
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Register the database models
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # route for index (home.html) web app starting point
    @app.route('/')
    def index():
        disclaimer_seen = request.cookies.get('cookie_name')
        return render_template('index.html', user_name=session.get('user_name'), disclaimer_seen=disclaimer_seen)

    # Import and register blueprints
    from routes.pokemon_routes import pokemon_bp
    from routes.neopets_routes import neopets_bp
    from routes.user_routes import user_bp
    from routes.magic_routes import magic_bp
    from routes.email_routes import email_bp

    # Register blueprints
    app.register_blueprint(pokemon_bp, url_prefix='/pokemon')
    app.register_blueprint(neopets_bp, url_prefix='/neopets')
    app.register_blueprint(magic_bp, url_prefix='/magic')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(email_bp, url_prefix='/email')
    app.register_blueprint(merchant_bp, url_prefix='/merchant')

    # Flask-Mail configuration
    app.config['SECRET_KEY'] = f'{FLASK_MAIL_KEY}'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = f'{FLASK_MAIL_EMAIL}'
    app.config['MAIL_PASSWORD'] = f'{FLASK_EMAIL_PASSWORD}'

    # eBay OAuth configurations FUTURE FEATURE
    #app.config['EBAY_APP_ID'] = 'your_ebay_app_id_here'
    #app.config['EBAY_CERT_ID'] = 'your_ebay_cert_id_here'
    #app.config['EBAY_DEV_ID'] = 'your_ebay_dev_id_here'
    #app.config['EBAY_RU_NAME'] = 'your_ebay_ru_name_here'

    # Return the app
    return app

# Run the app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
