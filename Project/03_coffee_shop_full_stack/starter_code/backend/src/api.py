import os
import sys
from flask import Flask, Request, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import werkzeug

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
db = SQLAlchemy()
app = Flask(__name__)
setup_db(app)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def convertRowToObject( row):
    result = {}
    for column in row.__table__.columns:
      result[column.name] = getattr(row, column.name)
    
    return result

def convertTableToList( table):
    result = []
    for row in table:
        rowObj = convertRowToObject(row)
        result.append(rowObj)
    
    return result
    
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
@cross_origin()
def getDrinks():
    try:
        data = db.session.query(Drink).all()
        listDrinks = convertTableToList(data)

        drinks = []

        for dict_drink in listDrinks:
            drink = Drink(id=dict_drink['id'],title=dict_drink["title"], recipe=dict_drink["recipe"])
            drinks.append(drink.short())

        return jsonify({
            'success':True,
            "drinks": drinks
        })
    except:
        print('error: ',sys.exc_info())
        abort(500)
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@cross_origin()
@requires_auth("get:drinks-detail")
def getDrinksDetail(self):
    try:
        data = Drink.query.all()
        listDrinks = convertTableToList(data)

        customList = []

        for dict_drink in listDrinks:
            drink = Drink(id=dict_drink['id'],title=dict_drink["title"], recipe=dict_drink["recipe"])
            customList.append(drink.long())

        return jsonify({
            'success':True,
            "drinks": customList
        })
    except:
        print('error: ',sys.exc_info())
        abort(500)
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@cross_origin()
@requires_auth("post:drinks")
def addDrinks(self):
    try:
        data = request.get_json()

        drink = Drink(title=data["title"], recipe=json.dumps(data["recipe"]))
        drink.insert()
        customDrink = convertRowToObject(drink)
        return jsonify({"success": True, "drinks": customDrink})
    except:
        print('error: ',sys.exc_info())
        abort(500)
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@cross_origin()
@requires_auth("patch:drinks")
def patchDrinks(self, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)
            return
        
        data = request.get_json()
        drink.recipe=json.dumps(data['recipe'])
        drink.title=data['title']
        drink.update()

        return jsonify({
            "success": True, "drinks": drink.long()
        })
    except:
        print('error: ',sys.exc_info())
        abort(500)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@cross_origin()
@requires_auth("delete:drinks")
def removeDrinks(self,id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
            return
        
        drink.delete()
        return jsonify({"success": True, "delete": id})
    except:
        print('error: ',sys.exc_info())
        abort(500)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def handle_not_found_error(e):
    return jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
                }), 404
app.register_error_handler(404, handle_not_found_error)
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response