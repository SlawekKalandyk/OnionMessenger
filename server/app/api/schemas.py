from marshmallow import Schema, fields, validate, pre_load, post_dump, post_load, ValidationError

from app.api.custom_fields import BytesField
from app.infrastructure.contact import Contact
from app.infrastructure.message import Message


class ContactSchema(Schema):
    __model__ = Contact

    contact_id = fields.Str()
    name = fields.Str(missing=None, allow_none=True)
    approved = fields.Bool()
    awaiting_approval = fields.Bool()
    address = fields.Str()

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class MessageSchema(Schema):
    __model__ = Message

    interlocutor = fields.Nested(ContactSchema())
    content = fields.Str()
    content_type = fields.Int()
    timestamp = fields.DateTime()
    message_author = fields.Int()
    message_state = fields.Int()

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)
