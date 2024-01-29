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
from models import db, User, People, Planets, FavoritePeople, FavoritePlanets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

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
    all_users = User.query.all()
    result = list(map(lambda item: item.serialize(), all_users))
    return jsonify(result), 200

@app.route('/people', methods=['GET'])
def view_people():
    all_people = People.query.all()
    result = list(map(lambda item: item.serialize(), all_people))
    return jsonify(result), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def view_person(people_id):
    people = People.query.filter_by(id=people_id).first()
    return jsonify(people.serialize()), 200

@app.route('/planets', methods=['GET'])
def view_planets():
    all_planets = Planets.query.all()
    result = list(map(lambda item: item.serialize(), all_planets))
    return jsonify(result), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def view_planet(planet_id):
    planet = Planets.query.filter_by(id=planet_id).first()
    return jsonify(planet.serialize()), 200

@app.route('/user/favorites', methods=['GET'])
def view_favorites():
    favorite_people = FavoritePeople.query.all()
    favorite_planets = FavoritePlanets.query.all()
    favorites = favorite_planets + favorite_people
    result = list(map(lambda item: item.serialize(), favorites))
    return jsonify(result), 200

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def create_favorite_person(people_id):
    body = request.get_json()
    favorite_person = FavoritePeople(people_name=body["people_name"],user_email=body["user_email"])
    db.session.add(favorite_person)
    db.session.commit()
    return jsonify(favorite_person.serialize()), 200

@app.route('/favorite/planet/<int:planets_id>', methods=['POST'])
def create_favorite_planet(planets_id):
    body = request.get_json()
    favorite_planet = FavoritePlanets(planets_name=body["planets_name"],user_email=body["user_email"])
    db.session.add(favorite_planet)
    db.session.commit()
    return jsonify(favorite_planet.serialize()), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    delete_favorite = FavoritePeople.query.filter_by(id=people_id).first()
    db.session.delete(delete_favorite)
    db.session.commit()
    return jsonify(), 200

@app.route('/favorite/planet/<int:planets_id>', methods=['DELETE'])
def delete_favorite_planet(planets_id):
    delete_favorite = FavoritePlanets.query.filter_by(id=planets_id).first()
    db.session.delete(delete_favorite)
    db.session.commit()
    return jsonify(), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)