from dataclasses import dataclass


@dataclass
class Contact:
    contact_id: str
    approved: bool
    awaiting_approval: bool