# This file contains the models for the MTG cards and collections. It also contains the relationship between the User and MTGCollection models.
from db_initialize import db

# Create a Magic: The Gathering card model
class MTGCard(db.Model):
    __tablename__ = 'mtg_cards'
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    mana_cost = db.Column(db.String(50))
    cmc = db.Column(db.Float)
    type_line = db.Column(db.String(255))
    oracle_text = db.Column(db.Text)
    colors = db.Column(db.String(50))
    color_identity = db.Column(db.String(50))
    set_name = db.Column(db.String(100))
    rarity = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    multiverse_id = db.Column(db.Integer, unique=True)

# Create a Magic: The Gathering collection junction table
class MTGCollection(db.Model):
    __tablename__ = 'mtg_collections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    card_id = db.Column(db.String(36), db.ForeignKey('mtg_cards.id'), nullable=False)  # Ensure this matches your card ID type

    # Make sure this matches the relationship name in the User model
    user = db.relationship('User', back_populates='mtg_collections')
    card = db.relationship('MTGCard', backref='collections')

