# This file contains the User model for the database
from db_initialize import db

# Create a User model
class User(db.Model):
    __tablename__ = 'users'  # Explicitly specify the table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_image = db.Column(db.String(120), nullable=True, default='default.jpg')

    # Relationships with cascade delete options
    neopets_collections = db.relationship('NeopetsCollection', back_populates='user', cascade="all, delete-orphan")
    collections = db.relationship('Collection', back_populates='user', cascade="all, delete-orphan")
    mtg_collections = db.relationship('MTGCollection', back_populates='user', cascade="all, delete-orphan")
