from app.shared.container import InstanceContainer
from app.messaging.base import Command, CommandMapper
from app.shared.helpful_abstractions import Singleton
from app.infrastructure.contact import Contact
from app.infrastructure.database import BaseModel
from peewee import BooleanField, Field, ForeignKeyField, IdentityField, PrimaryKeyField, TextField


class CommandField(Field):
    field_type = 'text'

    def db_value(self, value: Command):
        command_mapper: CommandMapper = InstanceContainer.resolve(CommandMapper)
        return command_mapper.map_to_json(value)

    def python_value(self, value: str):
        command_mapper: CommandMapper = InstanceContainer.resolve(CommandMapper)
        return command_mapper.map_from_json(value)


class SavedCommand(BaseModel):
    interlocutor = ForeignKeyField(Contact, backref='saved_commands')
    command = CommandField()
    identifier = TextField()
    initiate = BooleanField()

class SavedCommandRepository(metaclass=Singleton):
    def add(self, command: SavedCommand):
        command.save(force_insert=True)

    def get_by_identifier_and_contact(self, identifier: str, contact: Contact):
        return list(SavedCommand.select().where(SavedCommand.interlocutor.contact_id == contact.contact_id and SavedCommand.identifier == identifier))

    def get_all_initiating(self):
        return list(SavedCommand.select().where(SavedCommand.initiate == True))

    def get_by_command(self, command: Command):
        return SavedCommand.get_or_none(SavedCommand.command == command)

    def remove(self, command: SavedCommand):
        SavedCommand.delete_instance(command)