from app.messaging.messaging_receivers import AuthenticationReceiver
from app.messaging.base import Command
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass(frozen=True)
class AuthenticationCommand(Command):
    @classmethod
    def get_identifier(cls) -> str:
        return 'AUTHENTICATION'

    def invoke(self, receiver: AuthenticationReceiver):
        pass