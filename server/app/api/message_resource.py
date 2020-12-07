from flask_restful import Resource
from dataclasses import dataclass
from dataclasses_json import dataclass_json

from app.infrastructure.message import Message

@dataclass
@dataclass_json
class MessageDTO:
    def map_to_message(self):
        pass

    @staticmethod
    def map_from_message(message: Message):
        pass


class MessageResource(Resource):
    def __init__(self):
       pass

    def get(self, id=None):
        pass