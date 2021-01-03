from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
import datetime

from app.messaging.base import Command
from app.messaging.messaging_commands import AuthenticationCommand, InitiationCommand, SingleUseCommand
from app.infrastructure.message import ContentType, MessageAuthor, MessageState, Message
from app.infrastructure.contact import Contact
from app.api.receivers import MessageCommandReceiver, HelloCommandReceiver, ApproveCommandReceiver
from app.api.socket_emitter import emit_message, emit_contact


@dataclass_json
@dataclass(frozen=True)
class MessageCommand(Command):
    content: str
    content_type: ContentType

    @classmethod
    def get_identifier(cls) -> str: 
        return 'MESSAGE'

    def invoke(self, receiver: MessageCommandReceiver) -> List[Command]:
        contact: Contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        if contact and contact.approved and not contact.awaiting_approval:
            message = Message(interlocutor=contact, content=self.content, content_type=self.content_type, \
                timestamp=datetime.datetime.now(), message_author=MessageAuthor.INTERLOCUTOR, message_state=MessageState.RECEIVED)
            receiver.message_repository.add(message)
            emit_message(message)
        return []


@dataclass_json
@dataclass(frozen=True)
class HelloCommand(InitiationCommand, SingleUseCommand):
    @classmethod
    def get_identifier(cls) -> str:
        return 'HELLO'

    def invoke(self, receiver: HelloCommandReceiver) -> List[Command]:
        print("Inside HelloCommand invoke")
        new_contact = Contact(contact_id=self.source.split('.')[0], approved=False, awaiting_approval=True, address=self.source)
        receiver.contact_repository.add(new_contact)
        emit_contact(new_contact)
        # close connection - HelloCommand should be single-use only
        receiver.topology.remove(self.initiation_context.agent)
        self.initiation_context.agent.close_sockets()
        return []


@dataclass_json
@dataclass(frozen=True)
class ApproveCommand(InitiationCommand):
    approved: bool = False

    @classmethod
    def get_identifier(cls) -> str:
        return 'APPROVE'

    def invoke(self, receiver: ApproveCommandReceiver) -> List[Command]:
        contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        # if approval was sent from someone who is not in your contacts, ignore it and close sockets
        if not contact:
            receiver.topology.remove(self.initiation_context.agent)
            self.initiation_context.agent.close_sockets()
            return []
        contact.approved = self.approved
        contact.awaiting_approval = False
        receiver.contact_repository.update(contact)
        emit_contact(contact)
        # if approved, open socket for sending messages since a receiving one is already open
        if self.approved:
            auth_command = AuthenticationCommand()
            return [auth_command]
        return []
