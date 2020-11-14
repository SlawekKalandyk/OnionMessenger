from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.infrastructure.contact import Contact

class MessageState(Enum):
    SENT = 1
    RECEIVED = 2

@dataclass
class Message:
    content: str
    interlocutor: Contact
    timestamp: datetime
    state: MessageState