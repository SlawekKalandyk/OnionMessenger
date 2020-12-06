from dataclasses import dataclass
from peewee import BooleanField, TextField

from app.infrastructure.database import BaseModel


class Contact(BaseModel):
    contact_id = TextField(primary_key=True)
    approved = BooleanField()
    awaiting_approval = BooleanField()