from app.shared.signature import Signature
from app.networking.topology import Agent
from typing import List
from app.shared.config import TorConfiguration
from app.messaging.base import Command
from dataclasses import InitVar, dataclass, field
from dataclasses_json import dataclass_json


@dataclass(frozen=False)
class InitiationCommandContext:
    agent: Agent = None

    def initialize(self, agent: Agent):
        self.agent = agent


@dataclass_json
@dataclass(frozen=True)
class InitiationCommand(Command):
    source: str = f'{TorConfiguration.get_hidden_service_id()}.onion'
    initiation_context: InitVar[InitiationCommandContext] = field(default=InitiationCommandContext(),
                                                                init=False)
    signed_message: str = field(init=False)

    def __post_init__(self):
        self.signed_message = self._get_signed_message()

    def _get_signed_message(self) -> str:
        signature = Signature()
        return signature.sign(self.get_identifier())

    def _verify(self, public_key: str,  signed_message: str) -> bool:
        signature = Signature()
        return signature.verify(public_key, signed_message) == self.get_identifier()


@dataclass_json
@dataclass(frozen=True)
class SingleUseCommand(Command):
    pass
