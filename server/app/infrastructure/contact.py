from dataclasses import dataclass
from peewee import BooleanField, TextField

from app.infrastructure.database import BaseModel
from app.shared.helpful_abstractions import Singleton


class Contact(BaseModel):
    contact_id = TextField(primary_key=True)
    name = TextField()
    approved = BooleanField()
    awaiting_approval = BooleanField()
    address = TextField()


class ContactRepository(metaclass=Singleton):
    def add(self, contact: Contact):
        contact.save(force_insert=True)

    def get_messages(self, contact: Contact):
        return contact.messages

    def get_by_id(self, id: str):
        return Contact.get_or_none(Contact.contact_id == id)

    def update(self, contact: Contact):
        contact.update()