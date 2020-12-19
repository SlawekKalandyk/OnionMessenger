from dataclasses import dataclass
from datetime import datetime
from enum import Enum, IntEnum
from peewee import Field, ForeignKeyField, TextField, TimestampField

from app.infrastructure.contact import Contact
from app.infrastructure.database import BaseModel
from app.shared.helpful_abstractions import Singleton

class MessageState(IntEnum):
    SENT = 1
    RECEIVED = 2


class MessageAuthor(IntEnum):
    SELF = 1
    INTERLOCUTOR = 2


class ContentType(IntEnum):
    STRING = 1
    IMAGE = 2
    
    
class MessageStateField(Field):
    field_type = 'integer'
    
    def db_value(self, value: MessageState):
        return value

    def python_value(self, value: int):
        return MessageState(value)


class MessageAuthorField(Field):
    field_type = 'integer'
    
    def db_value(self, value: MessageAuthor):
        return value

    def python_value(self, value: int):
        return MessageAuthor(value)


class ContentTypeField(Field):
    field_type = 'integer'
    
    def db_value(self, value: ContentType):
        return value

    def python_value(self, value: int):
        return ContentType(value)


class Message(BaseModel):
    interlocutor = ForeignKeyField(Contact, backref='messages')
    content = TextField()
    content_type = ContentTypeField()
    timestamp = TimestampField()
    message_author = MessageAuthorField()
    message_state = MessageStateField()


class MessageRepository(metaclass=Singleton):
    def add(self, message: Message):
        message.save()