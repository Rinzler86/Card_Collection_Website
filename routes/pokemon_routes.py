# This file contains the routes for the Pokémon TCG API and the user's collection.
from flask import render_template, request, url_for, redirect, flash, session, Blueprint
from datetime import datetime
from flask import jsonify
from pokemon_api import get_or_fetch_card
from pokemon_models import Collection, Card
from db_initialize import db
from ignore_creds import TCG_API_KEY
from security import safe_requests

# Create a blueprint for the Pokémon TCG routes
pokemon_bp = Blueprint('pokemon', __name__)


# Create a route to fetch and display Pokémon TCG cards rarities
def fetch_rarities():
    """Fetch all possible card rarities from the Pokémon TCG API."""
    endpoint_url = "https://api.pokemontcg.io/v2/rarities"
    headers = {"X-Api-Key": TCG_API_KEY}
    response = safe_requests.get(endpoint_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        rarities = data.get('data', [])
        return rarities
    else:
        print(f"Failed to fetch rarities: {response.status_code}")
        return []

# Create a route to fetch and display Pokémon TCG cards sets
def fetch_sets():
    """Fetch all sets from the Pokémon TCG API."""
    endpoint_url = "https://api.pokemontcg.io/v2/sets"
    headers = {"X-Api-Key": TCG_API_KEY}
    response = safe_requests.get(endpoint_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('data', [])
    return []


# Create a route to fetch and display Pokémon TCG cards
def fetch_pokemon_data(query, limit=None):
    """Fetch Pokémon cards data based on a query, with an optional limit."""
    # If a limit is provided, use it to limit the results per page. Otherwise, fetch default number of results.
    endpoint_url = f"https://api.pokemontcg.io/v2/cards?q={query}"
    if limit:
        endpoint_url += f"&pageSize={limit}"

    headers = {"X-Api-Key": TCG_API_KEY}
    response = safe_requests.get(endpoint_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Return only the number of results specified by limit, if it's provided.
        return data.get('data', [])[:limit] if limit else data.get('data', [])
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return []


# Create a route to fetch and display Pokémon TCG cards
@pokemon_bp.route('/cards', methods=['GET', 'POST'])
def cards():
    # Fetch all sets and sort them by release date
    sets = fetch_sets()  # Fetch all sets
    sets.sort(key=lambda s: datetime.strptime(s['releaseDate'], '%Y/%m/%d'))

    # Fetch all card rarities
    from_year = request.form.get('from_year', str(1999))
    to_year = request.form.get('to_year', str(datetime.now().year))
    selected_set = request.form.get('set', '')
    pokemon_name = request.form.get('pokemon_name', '')

    # Filter sets based on the selected year range
    from_year_int = int(from_year)
    to_year_int = int(to_year)

    # Filter sets based on the selected year range
    sets_within_year_range = [
        s for s in sets if from_year_int <= datetime.strptime(s['releaseDate'], '%Y/%m/%d').year <= to_year_int
    ]

    cards = []
    query_parts = []
    if pokemon_name:
        query_parts.append(f"name:{pokemon_name}*")
    if selected_set:
        query_parts.append(f"set.id:{selected_set}")
    query = " AND ".join(query_parts)

    if request.method == 'POST':
        # Fetch initial 24 cards on first visit or based on the query if there's one
        limit = 24 if not query_parts else None
        cards = fetch_pokemon_data(query, limit=limit)
        cards.sort(key=lambda card: datetime.strptime(card.get('set', {}).get('releaseDate'), '%Y/%m/%d'))

    return render_template('pokemon_cards.html', cards=cards, sets=sets_within_year_range, pokemon_name=pokemon_name,
                           selected_set=selected_set, from_year=from_year, to_year=to_year)


# Create a route to add Pokémon TCG cards to the user's collection
@pokemon_bp.route('/add_to_collection/<string:card_id>', methods=['POST'])
def add_to_collection(card_id):
    if 'user_id' not in session:
        return jsonify({'error': 'You must be logged in to add cards to your collection.'}), 401

    user_id = session.get('user_id')
    condition = request.form.get('condition')

    card = get_or_fetch_card(card_id)
    if not card:
        return jsonify({'error': 'Card not found.'}), 404

    existing_collection = Collection.query.filter_by(user_id=user_id, card_id=card.id).first()
    if existing_collection:
        return jsonify({'info': 'This card is already in your collection.', 'alreadyInCollection': True}), 200

    new_collection_entry = Collection(user_id=user_id, card_id=card.id, condition=condition)
    db.session.add(new_collection_entry)
    db.session.commit()

    return jsonify({'success': 'Card successfully added to your collection.', 'added': True, 'card_id': card_id}), 200


# Create a route to view the user's Pokémon TCG collection
@pokemon_bp.route('/collection')
def view_collection():
    if 'user_id' not in session:
        flash('You must be logged in to view your collection.', 'warning')
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')
    # Assuming the Collection model has a user relationship to access the User's collections
    user_collections = Collection.query.filter_by(user_id=user_id).all()

    # Optionally, enrich the collection data with more details from the Card model if needed
    collections_with_details = []
    for collection_item in user_collections:
        card = Card.query.filter_by(id=collection_item.card_id).first()
        collections_with_details.append({
            'card_id': card.id,
            'name': card.name,
            'image_url': card.image_url,
            'condition': collection_item.condition,
            'normal_price_low': card.normal_price_low,
            'normal_price_mid': card.normal_price_mid,
            'normal_price_high': card.normal_price_high
        })

    return render_template('pokemon_collection.html', collections=collections_with_details)


# Create a route to remove Pokémon TCG cards from the user's collection
@pokemon_bp.route('/remove_from_collection', methods=['POST'])
def remove_from_collection():
    # Ensure the request is JSON and retrieve data accordingly
    if not request.is_json:
        print("Request is not JSON.")
        return jsonify({'removed': False, 'message': 'Request must be JSON.'}), 400

    data = request.get_json()  # Get the JSON data sent with the request
    card_id = data.get('card_id')
    user_id = session.get('user_id') # Get the user ID from the session

    print(f"Current session user_id: {user_id}, card_id: {card_id}")  # Debugging

    if not card_id or not user_id:
        return jsonify({'removed': False, 'message': 'Missing card ID or not logged in.'}), 400

    # Attempt to find the card in the user's collection
    try:
        # Attempt to find the card in the user's collection
        card_to_remove = Collection.query.filter_by(user_id=user_id, card_id=card_id).first()
        if card_to_remove:
            db.session.delete(card_to_remove)
            db.session.commit()
            return jsonify({'removed': True, 'message': 'Card successfully removed from collection.'})
        else:
            # The card was not found in the user's collection
            return jsonify({'removed': False, 'message': 'Card not found in collection.'}), 404
    except Exception as e:
        # Handle any errors that occur during the process
        print(f"Error: {str(e)}")
        return jsonify({'removed': False, 'message': str(e)}), 500
