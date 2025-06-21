from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from flasgger import Swagger, swag_from

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/intern")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwtsecretkey")

# adding swagger UI for easy testing of api end points
app.config['SWAGGER'] = {
    'title': 'User Management API',
    'uiversion': 3,
    'swagger_version': '2.0',
    'specs_route': '/apidocs/',
    'securityDefinitions': {
        'Bearer': {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    'security': [{'Bearer': []}]
}
swagger = Swagger(app)

mongo = PyMongo(app)
jwt = JWTManager(app)
#login and access token
@app.route('/auth/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        '200': {'description': 'Successfully logged in, returns access token.'},
        '401': {'description': 'Bad credentials.'}
    }
})
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = mongo.db.users.find_one({'email': email})
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'Bad credentials'}), 401

@app.route('/users', methods=['POST'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Create a new user (register).',
    'parameters': [
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'id': 'User',
                'required': ['name', 'email', 'password'],
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string', 'format': 'password'}
                }
            }
        }
    ],
    'responses': {
        '201': {'description': 'User created successfully.'},
        '400': {'description': 'Missing fields.'},
        '409': {'description': 'Email already exists.'}
    }
})
#create user
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (name and email and password):
        return jsonify({'msg': 'Missing fields'}), 400
    if mongo.db.users.find_one({'email': email}):
        return jsonify({'msg': 'Email already exists'}), 409
    hashed_password = generate_password_hash(password)
    user_id = mongo.db.users.insert_one({'name': name, 'email': email, 'password': hashed_password}).inserted_id
    return jsonify({'id': str(user_id), 'name': name, 'email': email}), 201
#get all users
@app.route('/users', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get a list of all users.',
    'security': [
        {
            "Bearer": []
        }
    ],
    'responses': {
        '200': {'description': 'A list of all users.'}
    }
})
#get all users
def get_users():
    users = mongo.db.users.find()
    result = []
    for user in users:
        result.append({'id': str(user['_id']), 'name': user['name'], 'email': user['email']})
    return jsonify(result), 200

@app.route('/users/<id>', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Get a single user by their ID.',
    'security': [
        {
            "Bearer": []
        }
    ],
    'parameters': [
        {'name': 'id', 'in': 'path', 'required': True, 'type': 'string'}
    ],
    'responses': {
        '200': {'description': 'User details.'},
        '404': {'description': 'User not found.'}
    }
})
#get a single user
def get_user(id):
    user = mongo.db.users.find_one({'_id': ObjectId(id)})
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    return jsonify({'id': str(user['_id']), 'name': user['name'], 'email': user['email']}), 200

@app.route('/users/<id>', methods=['PUT'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Update a user\'s details.',
    'security': [
        {
            "Bearer": []
        }
    ],
    'parameters': [
        {'name': 'id', 'in': 'path', 'required': True, 'type': 'string'},
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string', 'format': 'password'}
                }
            }
        }
    ],
    'responses': {
        '200': {'description': 'User updated successfully.'},
        '400': {'description': 'No data to update.'},
        '404': {'description': 'User not found.'}
    }
})
# update user details
def update_user(id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    update_data = {}
    if name:
        update_data['name'] = name
    if email:
        update_data['email'] = email
    if password:
        update_data['password'] = generate_password_hash(password)
    if not update_data:
        return jsonify({'msg': 'No data to update'}), 400
    result = mongo.db.users.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    if result.matched_count == 0:
        return jsonify({'msg': 'User not found'}), 404
    return jsonify({'msg': 'User updated'}), 200

@app.route('/users/<id>', methods=['DELETE'])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'summary': 'Delete a user.',
    'security': [
        {
            "Bearer": []
        }
    ],
    'parameters': [
        {'name': 'id', 'in': 'path', 'required': True, 'type': 'string'}
    ],
    'responses': {
        '200': {'description': 'User deleted successfully.'},
        '404': {'description': 'User not found.'}
    }
})
#delete user
def delete_user(id):
    result = mongo.db.users.delete_one({'_id': ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({'msg': 'User not found'}), 404
    return jsonify({'msg': 'User deleted'}), 200

# main function
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True) 