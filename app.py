from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from marshmallow import ValidationError

from blacklist import BLACKLIST
from db import db
from resources.ocurrence import Occurrence, OccurrenceList
from resources.user import UserRegister, User, UserLogin, UserLogout

app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("config")  # load default configs from default_config.py
app.config.from_envvar(
    "APPLICATION_SETTINGS"
)  # override with config.py (APPLICATION_SETTINGS points to config.py)
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)


# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


api.add_resource(Occurrence, "/occurrence", "/occurrence/<int:_id>", "/occurrence/search/<string:search_term>")
api.add_resource(OccurrenceList, "/occurrences")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")

if __name__ == "__main__":
    db.init_app(app)
    db.app = app

    # Start Flask APP
    app.run(port=5000, host='0.0.0.0')
