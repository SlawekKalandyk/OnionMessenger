
from app.messaging.messaging_commands import InitiationCommand
from dataclasses import InitVar, dataclass, field
from dataclasses_json import dataclass_json
from re import search
from typing import Any, Dict, List, Tuple
import datetime

from app.networking.topology import Agent
from app.messaging.base import Command
from app.infrastructure.message import ContentType, MessageAuthor, MessageState, Message
from app.infrastructure.contact import Contact
from app.api.receivers import ImAliveReceiver, MessageCommandReceiver, HelloCommandReceiver, ApproveCommandReceiver
from app.api.socket_emitter import emit_contact_online, emit_message, emit_contact


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


@dataclass(frozen=False)
class HelloCommandContext:
    agent: Agent = None

    def initialize(self, agent: Agent):
        self.agent = agent

@dataclass_json
@dataclass(frozen=True)
class HelloCommand(InitiationCommand):
    helloContext: InitVar[HelloCommandContext] = field(default=HelloCommandContext(),
                                             init=False)

    @classmethod
    def get_identifier(cls) -> str:
        return 'HELLO'

    def invoke(self, receiver: HelloCommandReceiver) -> List[Command]:
        print("Inside HelloCommand invoke")
        new_contact = Contact(contact_id=self.source.split('.')[0], approved=False, awaiting_approval=True, address=self.source)
        receiver.contact_repository.add(new_contact)
        emit_contact(new_contact)
        self.helloContext.agent.socket.close()
        return []


@dataclass_json
@dataclass(frozen=True)
class ApproveCommand(Command):
    approved: bool

    @classmethod
    def get_identifier(cls) -> str:
        return 'APPROVE'

    def invoke(self, receiver: ApproveCommandReceiver) -> List[Command]:
        contact = receiver.contact_repository.get_by_address(self.context.sender.address)
        contact = contact if contact else Contact(contact_id=self.context.sender.address.split('.')[0], address=self.context.sender.address)
        contact.approved = self.approved
        contact.awaiting_approval = False
        receiver.contact_repository.update(contact)
        emit_contact(contact)
        return []



# Change ImAlive to do nothing on invoke, move it to networking and separate into Networking commands and Domain commands
@dataclass_json
@dataclass(frozen=True)
class ImAliveCommand(Command):
    @classmethod
    def get_identifier(cls) -> str:
        return 'IMALIVE'
    
    def invoke(self, receiver: ImAliveReceiver) -> List[Command]:
        return []