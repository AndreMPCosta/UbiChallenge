from marshmallow import post_load

from ma import ma
from models.occurrence import OccurrenceModel


class OccurrenceSchema(ma.ModelSchema):
    class Meta:
        model = OccurrenceModel
        dump_only = ("id", "state", "location",)
        exclude = ("geo",)

    @post_load
    def _post_load(self, occurrence: OccurrenceModel):
        if 'category' in occurrence:
            occurrence['category'] = occurrence['category'].upper()
        return occurrence
