# This file contains the routes for the Neopets section of the website.
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from db_initialize import db
from neopets_models import NeopetCard, NeopetSet, NeopetsCollection

# Create a blueprint for the Neopets routes
neopets_bp = Blueprint('neopets', __name__)


# Create a route to fetch and display Neopets cards
@neopets_bp.route('/neopets', methods=['GET', 'POST'])
def neopets():
    # Fetch the sets and cards
    selected_set = request.form.get('set', '')
    search_name = request.form.get('name', '')
    is_searching = 'search' in request.form  # Detect if it's a search operation

    query = NeopetCard.query

    # Apply filters based on user input
    if selected_set:
        query = query.filter(NeopetCard.set_id == selected_set)
    if search_name:
        query = query.filter(NeopetCard.name.ilike(f"%{search_name}%"))

    # Apply limit only for the initial load, not for searches or specific set selections
    if not is_searching and not selected_set and not search_name:
        items = query.limit(24).all()
    else:
        items = query.all()

    sets = NeopetSet.query.all()

    # Prepare the data to be sent to the template
    items_data = [{
        'id': item.id,
        'name': item.name.title(),
        'set_name': NeopetSet.query.filter_by(id=item.set_id).first().name if item.set_id else "No Set",
        'image_url': url_for('static', filename=item.image_path.replace("\\", "/").replace("downloaded_images/",
                                                                                           "neopets_images/downloaded_images/"))
    } for item in items]

    sets_data = [{'id': set.id, 'name': set.name} for set in sets]

    # Render the template with the cards and sets
    return render_template('neopets_cards.html', items=items_data, sets=sets_data, selected_set=selected_set,
                           search_name=search_name, is_searching=is_searching)


# Create a route to view the user's Neopets collection
@neopets_bp.route('/view_neopets_collection')
def view_neopets_collection():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to view your collection.', 'warning')
        return redirect(url_for('user.login'))

    user_id = session.get('user_id')

    user_collections = NeopetsCollection.query.filter_by(user_id=user_id).all()

    collections_with_details = []
    for collection_item in user_collections:
        if neopet_card := NeopetCard.query.filter_by(id=collection_item.neopet_card_id).first():
            set_entry = NeopetSet.query.filter_by(id=neopet_card.set_id).first()
            set_name = set_entry.name if set_entry else "Unknown Set"
            collections_with_details.append({
                'neopet_card_id': neopet_card.id,
                'name': neopet_card.name.title(),
                'image_path': neopet_card.image_path,
                'set_name': set_name.title()
            })

    # Render the template with the collection details
    return render_template('neopets_collection.html', collections=collections_with_details)


# Create a route to remove Neopets cards from the user's collection
@neopets_bp.route('/remove_from_neopets_collection/<int:neopet_card_id>', methods=['POST'])
def remove_from_neopets_collection(neopet_card_id):
    if 'user_id' not in session:
        return jsonify({'removed': False, 'message': 'You must be logged in to remove items.'}), 401

    if collection_item := NeopetsCollection.query.filter_by(user_id=session['user_id'],
                                                        neopet_card_id=neopet_card_id).first():
        db.session.delete(collection_item)
        db.session.commit()
        return jsonify({'removed': True}), 200
    else:
        return jsonify({'removed': False, 'message': 'Item not found in collection.'}), 404


# Create a route to add Neopets cards to the user's collection
@neopets_bp.route('/add_neopet_to_collection/<int:neopet_card_id>', methods=['POST'])
def add_neopet_to_collection(neopet_card_id):
    if 'user_id' not in session:
        # Return an error JSON response if the user is not logged in
        return jsonify({'error': 'You must be logged in to add cards to your collection.'}), 401

    user_id = session.get('user_id')

    # Check if the card is already in the collection
    if existing_entry := NeopetsCollection.query.filter_by(user_id=user_id, neopet_card_id=neopet_card_id).first():
        # Return JSON indicating the card is already in the collection
        return jsonify({'added': False, 'alreadyInCollection': True}), 200

    # Add the card to the collection
    new_entry = NeopetsCollection(user_id=user_id, neopet_card_id=neopet_card_id)
    db.session.add(new_entry)
    db.session.commit()

    # Return a success JSON response
    return jsonify({'added': True, 'alreadyInCollection': False}), 200
