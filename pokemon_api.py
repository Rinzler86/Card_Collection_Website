# Description: This file contains functions to interact with the Pokémon TCG API.
import requests
from db_initialize import db
from pokemon_models import Card
from ignore_creds import TCG_API_KEY

# Retrieve rarities from the Pokémon TCG API
def fetch_rarities():
    """Fetch all possible card rarities from the Pokémon TCG API."""
    url = "https://api.pokemontcg.io/v2/rarities"
    headers = {"X-Api-Key": TCG_API_KEY}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json().get('data', [])
    else:
        return []

# Retrieve all Pokémon sets from the Pokémon TCG API
def fetch_sets():
    """Fetch all sets from the Pokémon TCG API."""
    url = "https://api.pokemontcg.io/v2/sets"
    headers = {"X-Api-Key": TCG_API_KEY}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json().get('data', [])
    else:
        return []

# Retrieve all Pokémon card data from the Pokémon TCG API
def fetch_pokemon_data(query):
    """Fetch Pokémon cards data based on a query."""
    url = f"https://api.pokemontcg.io/v2/cards?q={query}"
    headers = {"X-Api-Key": TCG_API_KEY}
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json().get('data', [])
    else:
        return []

# Retrieve a single Pokémon card from the Pokémon TCG API and store it in local database if it doesn't exist
def get_or_fetch_card(api_id):
    """Check if the card is in the database; if not, fetch from the API and store it."""
    # Check if the card already exists in the database

    # return the card if it exists
    if card := Card.query.filter_by(api_id=api_id).first():
        return card  # Return the card if it exists

    # Fetch card data from the Pokémon TCG API using the card's API ID
    url = f"https://api.pokemontcg.io/v2/cards/{api_id}"
    headers = {"X-Api-Key": TCG_API_KEY}
    response = requests.get(url, headers=headers)

    # Return None if the API call failed
    if not response.ok:
        return None  # Return None if the API call failed

    # Extract the card data from the API response
    data = response.json().get('data', {})

    # Extract relevant fields from the data
    new_card = Card(
        api_id=api_id,
        name=data.get('name'),
        image_url=data.get('images', {}).get('large'),
        rarity=data.get('rarity'),
        set_name=data.get('set', {}).get('name'),
        series=data.get('series'),
        types=",".join(data.get('types', [])),  # Join list into a comma-separated string
        prices_low=data.get('cardmarket', {}).get('prices', {}).get('lowPrice'),  # Example for extracting pricing
        prices_mid=data.get('cardmarket', {}).get('prices', {}).get('avgPrice'),
        prices_high=data.get('cardmarket', {}).get('prices', {}).get('trendPrice'),
        tcgplayer_id=data.get('tcgplayer', {}).get('productId'),
        # Add more fields as necessary
    )

    # Add the new card to the database
    db.session.add(new_card)
    db.session.commit()

    # Return the newly created card object
    return new_card

# Extract pricing information from the API response
def extract_prices(prices_data):
    """Extracts pricing information from the API response."""
    prices = {
        'normal_price_low': 0,
        'normal_price_mid': 0,
        'normal_price_high': 0,
        'reverse_holo_price_low': 0,
        'reverse_holo_price_mid': 0,
        'reverse_holo_price_high': 0,
    }
    # Extract pricing information from a normal card price in the API response
    if 'normal' in prices_data:
        prices['normal_price_low'] = prices_data['normal'].get('low', 0)
        prices['normal_price_mid'] = prices_data['normal'].get('mid', 0)
        prices['normal_price_high'] = prices_data['normal'].get('high', 0)

    # Extract pricing information from a reverse holofoil card price in the API response
    if 'reverseHolofoil' in prices_data:
        prices['reverse_holo_price_low'] = prices_data['reverseHolofoil'].get('low', 0)
        prices['reverse_holo_price_mid'] = prices_data['reverseHolofoil'].get('mid', 0)
        prices['reverse_holo_price_high'] = prices_data['reverseHolofoil'].get('high', 0)

    # Return the extracted pricing information
    return prices
