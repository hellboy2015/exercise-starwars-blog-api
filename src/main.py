"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorites
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
cors = CORS(app)
setup_admin(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
#@jwt_required()
def handle_planets():

    all_planets = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), all_planets))

    return jsonify(all_planets), 200

@app.route('/characters', methods=['GET'])
#@jwt_required()
def handle_characters():
    
    all_characters = Characters.query.all()
    all_characters = list(map(lambda x: x.serialize(), all_characters))

    return jsonify(all_characters), 200

@app.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    
    all_favorites = Favorites.query.all()
    all_favorites = list(map(lambda x: x.serialize(), all_favorites))

    return jsonify(all_favorites), 200

@app.route('/favorites', methods=['POST'])
@jwt_required()
def create_favorites():
    favoriteID = request.json.get("favoriteID", None)
    favoriteName = request.json.get("favoriteName", None)
    entityType = request.json.get("entityType", None)
    isFav = request.json.get("isFav", None)

    favorite = Favorites.query.filter_by(favoriteID=favoriteID).first()

    if favorite:
        # the user was not found on the database
        return jsonify({"msg": "favorite already exists"}), 401
    
    # busca usuario en BBDD
    # user = User.query.filter_by(email=email).first()
    
    # crea usuario nuevo
    # crea registro nuevo en BBDD de 
    favorite = Favorites(favoriteName=favoriteName, entityType=entityType, isFav=isFav, favoriteID=favoriteID)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "favorite created successfully"}), 200

@app.route('/favorites', methods=['DELETE'])
@jwt_required()
def remove_favorites():
    idToDelete = request.json.get("idToDelete", None)
    favorite = Favorites.query.get(idToDelete)
    if favorite is None:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(favorite)
    db.session.commit()
    
    response_body = {
        "msg": "favorite deleted successfully."
    }

    return jsonify(response_body), 200

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(username=username, password=password).first()

    if user is None:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@app.route('/register', methods=['POST'])
def handle_register():
    email = request.json.get("email", None)
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if email is None:
        return jsonify({"msg": "No email was provided"}), 400
    if password is None:
        return jsonify({"msg": "No password was provided"}), 400
    if username is None:
        return jsonify({"msg": "No username was provided"}), 400
    
    # busca usuario en BBDD
    user = User.query.filter_by(email=email).first()
    if user:
        # the user was not found on the database
        return jsonify({"msg": "User already exists"}), 401
    else:
        # crea usuario nuevo
        # crea registro nuevo en BBDD de 
        user1 = User(username=username, email=email, password=password, is_active=True)
        db.session.add(user1)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
