from app.shared.container import InstanceContainer
from app.networking.topology import Agent, Topology
from app.infrastructure.saved_command import SavedCommand, SavedCommandRepository
from app.shared.utility import get_onion_address_from_public_key
from app.shared.config import TorConfiguration
from app.shared.signature import Signature
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
import datetime

from app.messaging.base import Command
from app.messaging.messaging_commands import InitiationCommand, SaveableCommand, SingleUseCommand
from app.infrastructure.message import ContentType, MessageAuthor, MessageState, Message
from app.infrastructure.contact import Contact, ContactRepository
from app.api.receivers import AuthenticationReceiver, ConnectionEstablishedReceiver, MessageCommandReceiver, HelloCommandReceiver, ApproveCommandReceiver
from app.api.socket_emitter import emit_contact_online, emit_message, emit_new_contact_pending_self_approval, emit_received_contact_approval


@dataclass_json
@dataclass(frozen=True)
class MessageCommand(SaveableCommand):
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

    def save(self, address: str):
        super().save(address)
        # no need to save the same command again
        saved_command_repository = SavedCommandRepository()
        if saved_command_repository.get_by_command(self):
            return
        contact: Contact = ContactRepository().get_by_address(address)
        saved_command_repository.add(SavedCommand(interlocutor=contact, command=self, identifier=self.get_identifier(), initiate=False))

    def after_sending(self):
        saved_command_repository = SavedCommandRepository()
        saved_command = saved_command_repository.get_by_command(self)
        saved_command_repository.remove(saved_command)


@dataclass_json
@dataclass(frozen=True)
class HelloCommand(InitiationCommand, SingleUseCommand, SaveableCommand):
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

        contact_id = self.source.split('.')[0]
        contact = receiver.contact_repository.get_by_id(contact_id)
        if not contact:
            new_contact = Contact(contact_id=contact_id, approved=False, awaiting_approval=True, address=self.source, public_key=self.public_key)
            receiver.contact_repository.add(new_contact)
            emit_new_contact_pending_self_approval(new_contact)
            # contact is new, awaiting approval - close sockets
            self._close_sockets(receiver.topology, self.initiation_context.agent)
            return []
        else:
            # if approved, send approve, don't need to close sockets
            if contact.approved:
                approve_command = ApproveCommand(approved=contact.approved)
                return [approve_command]

            # if not approved - ignore for now
            self._close_sockets(receiver.topology, self.initiation_context.agent)
            return []
         
    def save(self, address: str):
        super().save(address)
        # only one hello per contact can be saved at once - more doesn't make sense
        saved_command_repository = SavedCommandRepository()
        contact: Contact = ContactRepository().get_by_address(address)
        if saved_command_repository.get_by_identifier_and_contact(self.get_identifier(), contact):
            return
        saved_command_repository.add(SavedCommand(interlocutor=contact, command=self, identifier=self.get_identifier(), initiate=True))

    def after_sending(self, address: str):
        topology: Topology = InstanceContainer.resolve(Topology)
        agent = topology.get_by_address(address)
        self._close_sockets(topology, agent)
        saved_command_repository = SavedCommandRepository()
        saved_command = saved_command_repository.get_by_command_and_address(self, address)
        if saved_command:
            saved_command_repository.remove(saved_command)


@dataclass_json
@dataclass(frozen=True)
class AuthenticationCommand(InitiationCommand):
    @classmethod
    def get_identifier(cls) -> str:
        return 'AUTHENTICATION'

    def invoke(self, receiver: AuthenticationReceiver) -> List[Command]:
        contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        # if authentication was sent from someone who is not in your contacts, ignore it and close sockets
        if not contact or not Signature.verify(contact.public_key, self.signed_uuid) or not contact.approved:
            self._close_sockets(receiver.topology, self.initiation_context.agent)
            return []

        emit_contact_online(contact)
        if not self.initiation_context.agent.send_socket:
            # TODO: send messages after establishing outgoing connection
            # if there's no outgoing connection, create one
            auth_command = AuthenticationCommand()
            return [auth_command]
        else:
            # if there is an outgoing connection, check if there are any backlogged messages, send ConnectionEstablishedCommand with messages
            saved_command_repository = SavedCommandRepository()
            messages = list(map(lambda x: x.command, saved_command_repository.get_by_identifier_and_contact(MessageCommand.get_identifier(), contact)))
            return messages + [ConnectionEstablishedCommand()]


@dataclass_json
@dataclass(frozen=True)
class ApproveCommand(InitiationCommand, SaveableCommand):
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

    def save(self, address: str):
        super().save(address)
        # only save if approved, since the other side needs to know we're approving
        # there should only be a single approve per contact for now
        if self.approved:
            saved_command_repository = SavedCommandRepository()
            contact: Contact = ContactRepository().get_by_address(address)
            if saved_command_repository.get_by_identifier_and_contact(self.get_identifier(), contact):
                return
            saved_command_repository.add(SavedCommand(interlocutor=contact, command=self, identifier=self.get_identifier(), initiate=True))

    def after_sending(self, address: str):
        if not self.approved:
            topology: Topology = InstanceContainer.resolve(Topology)
            agent = topology.get_by_address(address)
            self._close_sockets(topology, agent)
        saved_command_repository = SavedCommandRepository()
        saved_command = saved_command_repository.get_by_command_and_address(self, address)
        if saved_command:
            saved_command_repository.remove(saved_command)


@dataclass_json
@dataclass(frozen=True)
class ConnectionEstablishedCommand(Command):
    @classmethod
    def get_identifier(cls) -> str:
        return 'CONNESTBL'

    def invoke(self, receiver: ConnectionEstablishedReceiver):
        contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        saved_command_repository = SavedCommandRepository()
        messages = list(map(lambda x: x.command, saved_command_repository.get_by_identifier_and_contact(MessageCommand.get_identifier(), contact)))
        return messages