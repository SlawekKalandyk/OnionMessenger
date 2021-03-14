from app.shared.utility import get_onion_address_from_public_key
from app.shared.config import TorConfiguration
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
from app.api.socket_emitter import emit_contact_online, emit_message, emit_new_contact_pending_self_approval, emit_received_contact_approval


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
    public_key: str = TorConfiguration.get_hidden_service_public_key()

    @classmethod
    def get_identifier(cls) -> str:
        return 'HELLO'

    def invoke(self, receiver: HelloCommandReceiver) -> List[Command]:
        # if address derived from public key is not equal to received source address or signature can't be verified with received public key, ignore it and close sockets
        derived_address = get_onion_address_from_public_key(self.public_key)
        if derived_address != self.source or not Signature.verify(self.public_key, self.signed_uuid):
            self._close_sockets(receiver.topology, self.initiation_context.agent)
            return []

        new_contact = Contact(contact_id=self.source.split('.')[0], approved=False, awaiting_approval=True, address=self.source, public_key=self.public_key)
        receiver.contact_repository.add(new_contact)
        emit_new_contact_pending_self_approval(new_contact)
        # close connection - HelloCommand should be single-use only
        self._close_sockets(receiver.topology, self.initiation_context.agent)
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
        if not contact or not Signature.verify(contact.public_key, self.signed_uuid):
            self._close_sockets(receiver.topology, self.initiation_context.agent)
            return []

        # if there's no outgoing connection, create one
        emit_contact_online(contact)
        if not self.initiation_context.agent.send_socket:
            auth_command = AuthenticationCommand()
            return [auth_command]

        return []


@dataclass_json
@dataclass(frozen=True)
class ApproveCommand(InitiationCommand):
    approved: bool = False
    public_key: str = TorConfiguration.get_hidden_service_public_key()

    @classmethod
    def get_identifier(cls) -> str:
        return 'APPROVE'

    def invoke(self, receiver: ApproveCommandReceiver) -> List[Command]:
        # if address derived from public key is not equal to received source address or signature can't be verified with received public key, ignore it and close sockets
        derived_address = get_onion_address_from_public_key(self.public_key)
        if derived_address != self.source or not Signature.verify(self.public_key, self.signed_uuid):
            self._close_sockets(receiver.topology, self.initiation_context.agent)
            return []

        # if approval was sent from someone who is not in your contacts, ignore it and close sockets
        contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        if not contact:
            self._close_sockets(receiver.topology, self.initiation_context.agent)
            return []

        contact.public_key = self.public_key
        contact.approved = self.approved
        contact.awaiting_approval = False
        receiver.contact_repository.update(contact)
        
        # if approved, open socket for sending messages since a receiving one is already open
        if self.approved:
            emit_received_contact_approval(contact)
            auth_command = AuthenticationCommand()
            return [auth_command]
        # TODO: What to do when the other person disapproves? Give option to resend/remove?
        
        return []
