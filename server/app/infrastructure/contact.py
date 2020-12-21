from dataclasses import dataclass
from peewee import BooleanField, TextField

from app.infrastructure.database import BaseModel
from app.shared.helpful_abstractions import Singleton


class Contact(BaseModel):
    contact_id = TextField(primary_key=True)
    name = TextField(null=True)
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

    def get_all(self):
        return [x for x in Contact.select().dicts()]

    def get_all_approved(self):
        return Contact.select().where(Contact.approved and not Contact.awaiting_approval)

    def get_all_pending(self):
        return Contact.select().where(Contact.awaiting_approval)

    def get_all_blocked(self):
        return Contact.select().where(not Contact.approved and not Contact.awaiting_approval)

    def update(self, contact: Contact):
        contact.save()

    def remove(self, contact: Contact):
        Contact.delete_instance(contact.contact_id)