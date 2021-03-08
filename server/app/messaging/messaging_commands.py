from app.shared.utility import generate_random_guid
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
    signed_uuid: str = Signature.sign(TorConfiguration.get_hidden_service_private_key(), generate_random_guid())
    initiation_context: InitVar[InitiationCommandContext] = field(default=InitiationCommandContext(),
                                                                init=False)


@dataclass_json
@dataclass(frozen=True)
class SingleUseCommand(Command):
    pass
