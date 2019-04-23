import datetime
from typing import List

from geoalchemy2 import Geometry
from sqlalchemy import func

from db import db
from utils.lists import categories, states


class OccurrenceModel(db.Model):
    """An occurrence that should include its location and who reported it, default state is waiting validation"""

    __tablename__ = "occurrences"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=True)
    creation_date = db.Column(db.DateTime)
    update_date = db.Column(db.DateTime, nullable=True)
    state = db.Column(db.String(20), nullable=False)
    geo = db.Column(Geometry(geometry_type="POINT"))
    location = db.Column(db.String, nullable=True)
    author = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(20), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state = "Waiting Validation"

    @staticmethod
    def check_category(category):
        return category.upper() in categories

    @staticmethod
    def check_state(state):
        return state in states

    @staticmethod
    def get_occurrences_within_radius(location, radius):
        """Return all occurrences within a given radius (in meters) of this location."""
        return OccurrenceModel.query.filter(func.ST_Distance_Sphere(OccurrenceModel.geo, "POINT" + location)
                                            < int(radius)).all()

    @classmethod
    def find_by_id(cls, _id: int) -> "OccurrenceModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls) -> List["OccurrenceModel"]:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
