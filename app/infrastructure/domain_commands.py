from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Any, List

from app.messaging.commands import Command
from app.infrastructure.message import ContentType

@dataclass_json
@dataclass(frozen=True)
class MessageCommand(Command):
    content: bytes
    content_type: ContentType

    @classmethod
    def get_identifier(cls) -> str:
        return 'MESSAGE'

    # def invoke(self, receiver: DBSession) -> List[Command]:
    #     # check if sender_address is in approved
    #     # if it is, save message
    #     # else ignore it
    #     raise NotImplementedError