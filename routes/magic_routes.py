# This file contains the routes for the Magic: The Gathering card collection feature.
from flask import render_template, request, redirect, flash, session, Blueprint, jsonify, url_for
from sqlalchemy.exc import IntegrityError
import requests
from magic_api import get_all_cards, get_card_by_id, get_all_sets, get_cards_by_name
from magic_models import MTGCollection, MTGCard  # Assuming models for Magic cards and collections
from db_initialize import db
from flask import request, jsonify
from security import safe_requests


# Create a blueprint for the Magic: The Gathering routes
magic_bp = Blueprint('magic', __name__)

# Create a route to fetch and display Magic: The Gathering cards
def get_cards_by_set(set_code):
    base_url = "https://api.magicthegathering.io/v1/cards"
    request_url = f"{base_url}?set={set_code}"

    # Attempt to fetch the cards from the API
    try:
        response = safe_requests.get(request_url)
        if response.status_code == 200:
            # Extract the cards from the response
            cards_data = response.json().get('cards', [])
            return cards_data
        else:
            print("Failed to fetch data:", response.status_code)
            return []

    # Handle request exceptions
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return []

# Create a route to fetch and display Magic: The Gathering cards
@magic_bp.route('/magic/cards', methods=['GET', 'POST'])
def magic_cards():
    sets = get_all_sets()  # This should fetch all available sets to populate the dropdown.
    selected_set = request.args.get('set', '') if request.method == 'GET' else request.form.get('set', '')
    card_name = request.args.get('name', '') if request.method == 'GET' else request.form.get('name', '')

    # Fetch cards based on the selected set or card name
    cards = []

    # Check if a POST request was made or if a set or card name was provided
    if request.method == 'POST' or (selected_set or card_name):
        if card_name:
            cards = get_cards_by_name(card_name)  # Fetch cards by name if provided
        elif selected_set:
            cards = get_cards_by_set(selected_set)  # Fetch cards by set if selected
        else:
            cards = get_all_cards()  # Fetch all cards if no specific filter is applied
    else:
        cards = get_all_cards()  # Fetch all cards for initial GET request

    # Render the template with the cards and sets
    return render_template('magic_cards.html', cards=cards, sets=sets, selected_set=selected_set, card_name=card_name)


# Create a route to add Magic: The Gathering cards to the user's collection
@magic_bp.route('/magic/add_to_collection/<string:card_id>', methods=['POST'])
def add_magic_to_collection(card_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'You must be logged in to add cards to your collection.'}), 401

    user_id = session['user_id']
    # Assuming get_card_by_id makes an API call and returns card data
    card_data = get_card_by_id(card_id)
    if not card_data:
        return jsonify({'error': 'Card not found.'}), 404

    # Check if the card already exists in the database
    card_exists = db.session.query(MTGCard).filter_by(id=card_id).first() is not None

    # If the card does not exist, insert it into the database
    if not card_exists:
        try:
            new_card = MTGCard(
                id=card_id,
                name=card_data.get('name'),
                mana_cost=card_data.get('manaCost'),  # Make sure this matches your API's response structure
                rarity=card_data.get('rarity'),
                set_name=card_data.get('set'),  # Adjust according to actual API response field name
                image_url=card_data.get('imageUrl')  # Ensure this is the correct key for the image URL in your API's response
                # Add other fields as necessary
            )
            db.session.add(new_card)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'Failed to add card to the database.'}), 500

    # Check if card already in the user's collection
    existing_collection = MTGCollection.query.filter_by(user_id=user_id, card_id=card_id).first()
    if existing_collection:
        return jsonify({'info': 'This card is already in your collection.', 'alreadyInCollection': True}), 200

    # Add the card to the user's collection
    try:
        new_collection_entry = MTGCollection(user_id=user_id, card_id=card_id)
        db.session.add(new_collection_entry)
        db.session.commit()
        return jsonify({'success': 'Card successfully added to your collection.', 'added': True, 'card_id': card_id}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Failed to add card to your collection.'}), 500


# Create a route to view the user's Magic: The Gathering collection
@magic_bp.route('/magic/collection')
def view_magic_collection():
    if 'user_id' not in session:
        flash('You must be logged in to view your collection.', 'warning')
        return redirect(url_for('user.login'))

    user_id = session['user_id']
    # Assuming there's a relationship set up between MTGCollection and MTGCard
    user_collection = db.session.query(MTGCollection, MTGCard).join(MTGCard, MTGCollection.card_id == MTGCard.id).filter(MTGCollection.user_id == user_id).all()

    # Prepare collection details including image_url from the MTGCard model
    collection_details = [{
        'card_id': card.MTGCard.id,  # Make sure this is added
        'name': card.MTGCard.name,
        'image_url': card.MTGCard.image_url,
        'set_name': card.MTGCard.set_name,
        # Include other fields as needed
    } for card in user_collection]

    return render_template('magic_collection.html', collections=collection_details)


# Create a route to remove Magic: The Gathering cards from the user's collection
@magic_bp.route('/remove_from_collection/', methods=['POST'])
def remove_from_collection():
    print("Entered remove_from_collection route")  # Confirm route is being hit

    # Check if the user is logged in
    if 'user_id' not in session:
        print("User not logged in")
        return jsonify({'error': 'You must be logged in to remove cards from your collection.'}), 401

    user_id = session['user_id']
    print(f"User ID: {user_id}")  # Check the user ID

    # Attempt to print the incoming JSON payload
    print("Incoming JSON:", request.json)

    card_id = request.json.get('card_id')  # Assuming the card ID is sent in the request body
    print(f"Card ID from JSON: {card_id}")  # Check the extracted card ID

    # Check if the card ID is missing
    if not card_id:
        print("Card ID is missing")
        return jsonify({'error': 'Card ID is required.'}), 400

    # Fetch the specific collection entry
    collection_entry = MTGCollection.query.filter_by(user_id=user_id, card_id=card_id).first()

    # Check if the card exists in the user's collection
    if not collection_entry:
        print(f"No collection entry found for card ID: {card_id}")
        return jsonify({'error': 'Card not found in your collection.'}), 404

    print("Card ID from JSON:", card_id)

    # Attempt to remove the card from the collection
    try:
        # If the card exists in the collection, remove it
        print(f"Removing card ID {card_id} from collection")
        db.session.delete(collection_entry)
        db.session.commit()
        return jsonify({'success': 'Card successfully removed from your collection.', 'removed': True, 'card_id': card_id}), 200
    # Handle any exceptions that occur during the removal process
    except Exception as e:
        db.session.rollback()
        print(f"Exception occurred: {e}")  # Log the exception
        return jsonify({'error': 'An error occurred while removing the card from your collection.'}), 500



