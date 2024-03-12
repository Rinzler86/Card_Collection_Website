# This file contains the models for the neopets database
from db_initialize import db

# Create a Neopet set model
class NeopetSet(db.Model):
    __tablename__ = 'neopet_sets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

# Create a Neopet card model
class NeopetCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey('set.id'), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

# Create a Neopet collection junction table
class NeopetsCollection(db.Model):
    __tablename__ = 'neopets_collection'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    neopet_card_id = db.Column(db.Integer, db.ForeignKey('neopet_card.id'), nullable=False)

    user = db.relationship('User', back_populates='neopets_collections')
    neopet_card = db.relationship('NeopetCard', backref='neopets_collections')
