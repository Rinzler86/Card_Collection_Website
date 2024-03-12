# initialize the database
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Create the database object
db = SQLAlchemy()

# Create the CSRF protection object
csrf = CSRFProtect()
