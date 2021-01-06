from app.shared.signature import Signature
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
import datetime

from app.messaging.base import Command
from app.messaging.messaging_commands import InitiationCommand, SingleUseCommand
from app.infrastructure.message import ContentType, MessageAuthor, MessageState, Message
from app.infrastructure.contact import Contact
from app.api.receivers import AuthenticationReceiver, MessageCommandReceiver, HelloCommandReceiver, ApproveCommandReceiver
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
    public_key: str = Signature().get_public_key()

    @classmethod
    def get_identifier(cls) -> str:
        return 'HELLO'

    def invoke(self, receiver: HelloCommandReceiver) -> List[Command]:
        if not self._verify(self.public_key, self.signed_message):
            receiver.topology.remove(self.initiation_context.agent)
            self.initiation_context.agent.close_sockets()
            return []
        new_contact = Contact(contact_id=self.source.split('.')[0], approved=False, awaiting_approval=True, address=self.source, signature_public_key=self.public_key)
        receiver.contact_repository.add(new_contact)
        emit_contact(new_contact)
        # close connection - HelloCommand should be single-use only
        receiver.topology.remove(self.initiation_context.agent)
        self.initiation_context.agent.close_sockets()
        return []


@dataclass_json
@dataclass(frozen=True)
class AuthenticationCommand(InitiationCommand):
    @classmethod
    def get_identifier(cls) -> str:
        return 'AUTHENTICATION'

    def invoke(self, receiver: AuthenticationReceiver) -> List[Command]:
        contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        # if authentication was sent from someone who is not in your contacts, ignore it and close sockets
        if not contact or not self._verify(contact.signature_public_key, self.signed_message):
            receiver.topology.remove(self.initiation_context.agent)
            self.initiation_context.agent.close_sockets()
            return []
        if not self.initiation_context.agent.send_socket:
            auth_command = AuthenticationCommand()
            return [auth_command]
        return []


@dataclass_json
@dataclass(frozen=True)
class ApproveCommand(InitiationCommand):
    approved: bool = False
    public_key: str = Signature().get_public_key()

    @classmethod
    def get_identifier(cls) -> str:
        return 'APPROVE'

    def invoke(self, receiver: ApproveCommandReceiver) -> List[Command]:
        contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        if contact:
            contact.signature_public_key = self.public_key
        # if approval was sent from someone who is not in your contacts, ignore it and close sockets
        if not contact or not self._verify(contact.signature_public_key, self.signed_message):
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
