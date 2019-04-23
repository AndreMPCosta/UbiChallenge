import ast
import datetime
import re

from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from models.occurrence import OccurrenceModel
from models.user import UserModel
from schemas.ocurrence import OccurrenceSchema
from utils.lists import categories, states

occurrence_schema = OccurrenceSchema()
occurrence_list_schema = OccurrenceSchema(many=True)


def convert_filter(url_filter) -> str:
    # filtering for 2 parameters
    if url_filter.find('&') != -1:
        equal_sign = [m.start() for m in re.finditer('=', url_filter)]
        return "{" + "'{}':'{}', '{}':'{}'".format(url_filter[0:equal_sign[0]],
                                                   url_filter[equal_sign[0] + 1:url_filter.find('&')],
                                                   url_filter[url_filter.find('&') + 1:equal_sign[1]],
                                                   url_filter[equal_sign[1] + 1:]) + "}"
    else:
        return "{" + "'{}':'{}'".format(url_filter[0:url_filter.find('=')],
                                        url_filter[url_filter.find('=') + 1:]) + "}"


class Occurrence(Resource):
    @classmethod
    def get(cls, **kwargs):
        if '_id' in kwargs:
            # get occurrence by id
            occurrence = OccurrenceModel.find_by_id(kwargs['_id'])
            if occurrence:
                return occurrence_schema.dump(occurrence), 200
            else:
                return {"message": "Occurrence not found."}, 404
        else:
            # get occurrence by filtering
            custom_filter = ast.literal_eval(convert_filter(kwargs['search_term']))
            if len(custom_filter) == 1:
                # only one parameter
                occurrences = OccurrenceModel.query.filter_by(**custom_filter).all()
            else:
                # two parameters, so we are looking for a location within certain radius
                occurrences = OccurrenceModel.get_occurrences_within_radius(**custom_filter)
            if occurrences:
                return {"occurrences": occurrence_list_schema.dump(occurrences)}, 200
        return {"message": "There are no matches to your search criteria"}, 404

    @classmethod
    def post(cls):
        # create an occurrence with at least a location and an author
        occurrence_json = request.get_json()
        # check if location is present on the json
        if 'geo' in occurrence_json:
            # the way the data has to be stored using PostGIS
            location = "POINT({} {})".format(occurrence_json['geo']['latitude'],
                                             occurrence_json['geo']['longitude'])
        else:
            return {"message": "You need to specify a geolocation with latitude and longitude."}, 404
        if 'category' in occurrence_json:
            # check if category is valid
            if not OccurrenceModel.check_category(occurrence_json['category']):
                return {"message": "Invalid Category, please insert one of the following: {}".format(
                    ', '.join(categories))}, 404

        occurrence = occurrence_schema.load(occurrence_json)
        occurrence.location = "({} {})".format(occurrence_json['geo']['latitude'],
                                               occurrence_json['geo']['longitude'])
        occurrence.geo = location
        # Force Default state when creating an occurrence
        occurrence.state = "Waiting Validation"
        try:
            occurrence.save_to_db()
        except:
            return {"message": "Internal server error. Failed to create occurrence."}, 500
        return occurrence_schema.dump(occurrence), 201

    @classmethod
    @jwt_required
    def delete(cls, _id: int):
        # get current user using jwt identity
        current_user = get_jwt_identity()
        # check if the user has admin role
        if not UserModel.find_by_id(current_user).admin:
            return {"message": "You need Admin permissions to access this resource."}, 400
        occurrence = OccurrenceModel.find_by_id(_id)
        if occurrence:
            occurrence.delete_from_db()
            return {"message": "Occurrence deleted."}, 200
        return {"message": "Occurrence not found."}, 404

    @classmethod
    @jwt_required
    def put(cls, _id: int = None):
        # get current user using jwt identity
        current_user = get_jwt_identity()
        # check if user has permissions to update an occurrence
        if not UserModel.find_by_id(current_user).admin:
            return {"message": "You need Admin permissions to access this resource."}, 400
        occurrence_json = request.get_json()
        if _id:
            occurrence = OccurrenceModel.find_by_id(_id)
            if occurrence:
                # check for state in json
                if not 'state' in occurrence_json:
                    return {"message": "You need to specify the state of the occurrence."}, 404
                else:
                    # check if it is a valid state
                    if not occurrence.check_state(occurrence_json["state"]):
                        return {"message": "Invalid state. It should be one of the following: {}".format(
                            ', '.join(states))}, 404
                    # update state and refresh date
                    occurrence.state = occurrence_json["state"]
                    occurrence.update_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif not occurrence:
                return {"message": "Occurrence not found."}, 404
        else:
            # same as post method, we should be able to create an occurrence using PUT method
            # check if location is present on the json
            if 'geo' in occurrence_json:
                # the way the data has to be stored using PostGIS
                location = "POINT({} {})".format(occurrence_json['geo']['latitude'],
                                                 occurrence_json['geo']['longitude'])
            else:
                return {"message": "You need to specify a geolocation with latitude and longitude."}, 404
            if 'category' in occurrence_json:
                if not OccurrenceModel.check_category(occurrence_json['category']):
                    return {"message": "Invalid Category, please insert one of the following: {}".format(
                        ', '.join(categories))}, 404

            occurrence = occurrence_schema.load(occurrence_json)
            occurrence.location = "({} {})".format(occurrence_json['geo']['latitude'],
                                                   occurrence_json['geo']['longitude'])
            occurrence.geo = location
            # Force Default state when creating an occurrence
            occurrence.state = "Waiting Validation"
        try:
            occurrence.save_to_db()
        except:
            return {"message": "Internal server error. Failed to update/create occurrence."}, 500
        return occurrence_schema.dump(occurrence), 200


# fetch all occurrences
class OccurrenceList(Resource):
    @classmethod
    def get(cls):
        return {"occurrences": occurrence_list_schema.dump(OccurrenceModel.find_all())}, 200
