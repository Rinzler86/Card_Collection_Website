# Description: This file contains functions to interact with the Magic: The Gathering API.
import requests

# Define the base URL for the Magic: The Gathering API
API_BASE_URL = "https://api.magicthegathering.io/v1"

# Retrieve all Magic: The Gathering cards from the API
def get_all_cards(page=1, page_size=100):
    """Fetch a list of MTG cards with pagination."""
    url = f"{API_BASE_URL}/cards"
    params = {
        'page': page,
        'pageSize': page_size
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('cards', [])
    else:
        return []

# Retrieve a specific Magic: The Gathering card from the API using its ID
def get_card_by_id(card_id):
    """Fetch a specific MTG card by its ID."""
    url = f"{API_BASE_URL}/cards/{card_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('card', {})
    else:
        return {}

# Retrieve all Magic: The Gathering sets from the API
def get_all_sets():
    """Fetch a list of all MTG sets."""
    url = f"{API_BASE_URL}/sets"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('sets', [])
    else:
        return []

# Retrieve all Magic: The Gathering cards from the API using a specific name
def get_cards_by_name(name, page=1, page_size=100):
    """Fetch a list of MTG cards by name with pagination."""
    url = f"{API_BASE_URL}/cards"
    params = {
        'name': name,
        'page': page,
        'pageSize': page_size
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('cards', [])
    else:
        return []

