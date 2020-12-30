from app.networking.topology import Topology
from dataclasses import dataclass

from app.messaging.base import Receiver
from app.infrastructure.contact import ContactRepository
from app.infrastructure.message import MessageRepository


@dataclass
class MessageCommandReceiver(Receiver):
    contact_repository: ContactRepository
    message_repository: MessageRepository


@dataclass
class HelloCommandReceiver(Receiver):
    contact_repository: ContactRepository


@dataclass
class ApproveCommandReceiver(Receiver):
    contact_repository: ContactRepository


@dataclass
class ImAliveReceiver(Receiver):
    topology: Topology
    contact_repository: ContactRepository