from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Any, List

from app.messaging.commands import Command


@dataclass_json
@dataclass(frozen=True)
class HelloCommand(Command):
    @classmethod
    def get_identifier(cls) -> str:
        return 'HELLO'

    # def invoke(self, receiver: DBSession) -> List[Command]:
    #     # new_contact = Contact(sender_onion_address, False, True)
    #     # receiver.Contactsadd()
    #     # return []

    #     raise NotImplementedError


@dataclass_json
@dataclass(frozen=True)
class ApproveCommand(Command):
    approved: bool

    @classmethod
    def get_identifier(cls) -> str:
        return 'APPROVE'

    # def invoke(self, receiver: DBSession) -> List[Command]:
    #     # contact = receiver.Contacts.where(c => c.contact_id == sender_onion_address)
    #     # contact.approved = self.approved
    #     # contact.awaiting_approval = False
    #     # receiver.update(contact)
    #     # return []

    #     raise NotImplementedError