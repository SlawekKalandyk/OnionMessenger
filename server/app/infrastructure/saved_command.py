from app.shared.container import InstanceContainer
from app.messaging.base import Command, CommandMapper
from app.shared.helpful_abstractions import Singleton
from app.infrastructure.contact import Contact
from app.infrastructure.database import BaseModel
from peewee import Field, ForeignKeyField, TextField


class CommandField(Field):
    field_type = 'text'

    def db_value(self, value: Command):
        return value.to_json()

    def python_value(self, value: str):
        command_mapper: CommandMapper = InstanceContainer.resolve(CommandMapper)
        return command_mapper.map_from_json(value)


class SavedCommand(BaseModel):
    interlocutor = ForeignKeyField(Contact, backref='saved_commands')
    command = CommandField()
    identifier = TextField()


class SavedCommandRepository(metaclass=Singleton):
    def add(self, command: SavedCommand):
        command.save(force_insert=True)