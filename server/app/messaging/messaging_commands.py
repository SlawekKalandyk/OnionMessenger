from app.messaging.messaging_receivers import ImAliveCommandReceiver
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


@dataclass_json
@dataclass(frozen=True)
class ImAliveCommand(Command):
    """
    Command responsible for keeping the connection alive. When received mark responsible agent's time since last contact as 0.
    """
    @classmethod
    def get_identifier(cls) -> str:
        return 'IMALIVE'

    def invoke(self, receiver: ImAliveCommandReceiver):
        agent: Agent = receiver.topology.get_by_address(self.context.sender.address)
        if agent:
            agent.time_since_last_contact = 0