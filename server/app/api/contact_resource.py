from flask_restful import Resource
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from app.infrastructure.contact import Contact

@dataclass
@dataclass_json
class ContactDTO:
    def map_to_contact(self):
        pass

    @staticmethod
    def map_from_contact(contact: Contact):
        pass


class ContactResource(Resource):
    def __init__(self):
       pass

    def get(self, id=None):
        return 'a'