import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": formatted_drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_drinks(payload):
    newDrink = Drink(
        title=request.get_json()['title'],
        recipe=json.dumps(request.get_json()['recipe'])
    )

    newDrink.insert()
    return jsonify({
        "success": True,
        "drinks": [newDrink.long()]
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink(payload, id):
    if not Drink.query.get(id):
        abort(404)

    drink = Drink.query.filter_by(id=id).one_or_none()
    # drink = Drink.query.get(id)
    drink.title = request.get_json()['title']
#    drink.recipe = json.dumps(request.get_json()['recipe'])
    drink.recipe = recipe if type(recipe) == str else json.dumps(recipe)

    drink.update()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    if not Drink.query.get(id):
        abort(404)

    drink = Drink.query.filter_by(id=id).one_or_none()
    # drink = Drink.query.get(id)

    drink.delete()
    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
        }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    """
    error handler for AuthError
    """
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
