from db_initialize import db

# Create a Pokemon card model
class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    supertype = db.Column(db.String(100), nullable=True)
    subtypes = db.Column(db.Text, nullable=True)
    hp = db.Column(db.String(50), nullable=True)
    types = db.Column(db.Text, nullable=True)
    evolvesFrom = db.Column(db.String(255), nullable=True)
    abilities = db.Column(db.Text, nullable=True)
    attacks = db.Column(db.Text, nullable=True)
    weaknesses = db.Column(db.Text, nullable=True)
    retreatCost = db.Column(db.Text, nullable=True)
    set_id = db.Column(db.String(100), nullable=True)
    set_name = db.Column(db.String(255), nullable=True)
    rarity = db.Column(db.String(50), nullable=True)
    flavorText = db.Column(db.Text, nullable=True)
    nationalPokedexNumbers = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    prices = db.Column(db.Text, nullable=True)  # Consider changing this if you're handling prices differently now
    releaseDate = db.Column(db.Date, nullable=True)
    series = db.Column(db.String(255), nullable=True)
    symbol_url = db.Column(db.String(255), nullable=True)
    number = db.Column(db.String(50), nullable=True)
    artist = db.Column(db.String(255), nullable=True)
    tcgplayer_id = db.Column(db.String(255), nullable=True)
    cardmarket_id = db.Column(db.String(255), nullable=True)
    normal_price_low = db.Column(db.Float, nullable=True)
    normal_price_mid = db.Column(db.Float, nullable=True)
    normal_price_high = db.Column(db.Float, nullable=True)
    reverse_holo_price_low = db.Column(db.Float, nullable=True)
    reverse_holo_price_mid = db.Column(db.Float, nullable=True)
    reverse_holo_price_high = db.Column(db.Float, nullable=True)

    #pokemon card constructor
    def __init__(self, api_id, name, image_url, rarity=None, series=None, set_name=None, release_date=None, price=None,
                 **kwargs):
        print("Initializing Card with data:", api_id, name, kwargs)  # Debug print
        self.api_id = api_id
        self.name = name
        self.image_url = image_url
        self.rarity = rarity
        self.series = series
        self.set_name = set_name
        self.releaseDate = release_date
        self.price = price
        for key, value in kwargs.items():
            setattr(self, key, value)

 # Create a collection junction table
class Collection(db.Model):
    __tablename__ = 'collection'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id', ondelete='CASCADE'), primary_key=True)
    condition = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', back_populates='collections')
    card = db.relationship('Card', backref='collections')

