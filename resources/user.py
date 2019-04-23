import traceback

from flask import request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)
from flask_restful import Resource

from blacklist import BLACKLIST
from models.user import UserModel
from schemas.user import UserSchema
from utils.password_manager import encrypt_password, check_encrypted_password

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_json['password'] = encrypt_password(user_json['password'])
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username):
            return {"message": "A user with that username already exists."}, 400

        try:
            user.save_to_db()
            return {"message": "Account created successfully."}, 201
        except:  # failed to save user to db
            traceback.print_exc()
            user.delete_from_db()  # rollback
            return {"Internal server error. Failed to create user."}, 500


class User(Resource):
    """Internal usage for testing"""

    @classmethod
    @jwt_required
    def get(cls, user_id: int):
        current_user = get_jwt_identity()
        print(current_user)
        user = UserModel.find_by_id(current_user)
        print(user)
        if not user.admin:
            return {"message": "You need Admin permissions to access this resource."}
        search_user = UserModel.find_by_id(user_id)
        if not search_user:
            return {"message": "User not found."}, 404
        return user_schema.dump(search_user), 200

    @classmethod
    @jwt_required
    def delete(cls, user_id: int):
        current_user = get_jwt_identity()
        if not UserModel.find_by_id(current_user).admin:
            return {"message": "You need Admin permissions to access this resource."}
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404

        user.delete_from_db()
        return {"message": "User deleted."}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_json = request.get_json()
        user_data = user_schema.load(user_json)
        user = UserModel.find_by_username(user_data.username)
        if user and check_encrypted_password(user_data.password, user.password):
            access_token = create_access_token(user.id, fresh=True)
            return (
                {"access_token": access_token},
                200,
            )
        return {"message": "Invalid credentials!"}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        BLACKLIST.add(jti)
        return {"message": "User {} successfully logged out.".format(user.username)}, 200
