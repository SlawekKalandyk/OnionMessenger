from __future__ import annotations
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from re import search
from typing import Any, Dict, List, Tuple
import datetime

from app.messaging.base import Command
from app.messaging.receivers import MessageCommandReceiver, HelloCommandReceiver, ApproveCommandReceiver
from app.infrastructure.message import ContentType, MessageAuthor, MessageState, Message
from app.infrastructure.contact import Contact
from app.messaging.socket_emitter import emit_message, emit_contact


class CommandMapper:
    def __init__(self):
        self._registered_commands: Dict[str, type] = dict()

    def register(self, command_type: type) -> CommandMapper:
        identifier = command_type.get_identifier()
        self._registered_commands[identifier] = command_type
        return self

    def map_to_bytes(self, command: Command) -> bytes:
        self._assert_registered(command.get_identifier())
        code = command.to_json()
        return (command.get_identifier() + code).encode('utf-8')

    def map_from_bytes(self, data: bytes) -> Command:
        identifier, code = self._parse(data.decode('utf-8'))
        self._assert_registered(identifier)

        command_type = self._registered_commands[identifier]
        return command_type.from_json(code)

    def _parse(self, text: str) -> Tuple[str, str]:
        index = search(r'[^A-Z]', text).start()
        return text[:index], text[index:]

    def _assert_registered(self, identifier: str):
        if identifier not in self._registered_commands:
            raise CommandTypeNotRegisteredError(identifier)


class CommandTypeNotRegisteredError(Exception):
    pass


@dataclass_json
@dataclass(frozen=True)
class MessageCommand(Command):
    content: str
    content_type: ContentType

    @classmethod
    def get_identifier(cls) -> str:
        return 'MESSAGE'

    def invoke(self, receiver: MessageCommandReceiver) -> List[Command]:
        contact: Contact = receiver.contact_repository.get_by_id(self.source)
        if contact and contact.approved and not contact.awaiting_approval:
            message = Message(interlocutor=contact, content=self.content, content_type=self.content_type, \
                timestamp=datetime.datetime.now(), message_author=MessageAuthor.INTERLOCUTOR, message_state=MessageState.RECEIVED)
            receiver.message_repository.add(message)
            emit_message(message)
        return []


@dataclass_json
@dataclass(frozen=True)
class HelloCommand(Command):
    @classmethod
    def get_identifier(cls) -> str:
        return 'HELLO'

    def invoke(self, receiver: HelloCommandReceiver) -> List[Command]:
        new_contact = Contact(contact_id=self.source, approved=False, awaiting_approval=True, address=self.source)
        receiver.contact_repository.add(new_contact)
        emit_contact(new_contact)
        return []


@dataclass_json
@dataclass(frozen=True)
class ApproveCommand(Command):
    approved: bool

    @classmethod
    def get_identifier(cls) -> str:
        return 'APPROVE'

    def invoke(self, receiver: ApproveCommandReceiver) -> List[Command]:
        contact = receiver.contact_repository.get_by_id(self.source)
        contact = contact if contact else Contact(contact_id=self.source, address=self.source)
        contact.approved = self.approved
        contact.awaiting_approval = False
        receiver.contact_repository.update(contact)
        emit_contact(contact)
        return []