from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.infrastructure.contact import Contact


class MessageState(Enum):
    SENT = 1
    RECEIVED = 2


class MessageAuthor(Enum):
    SELF = 1
    INTEROLOCUTOR = 2


class ContentType(Enum):
    STRING = 1
    IMAGE = 2


@dataclass
class Message:
    message_id: int
    interlocutor: Contact
    content: any
    content_type: ContentType
    timestamp: datetime
    message_author: MessageAuthor
    message_state: MessageState
