from app.networking.base import ConnectionSettings
from app.shared.container import InstanceContainer
from app.messaging.broker import Broker, Payload
from app.networking.topology import Agent
from typing import List
from app.shared.config import TorConfiguration
from app.messaging.messaging_receivers import AuthenticationReceiver
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


@dataclass_json
@dataclass(frozen=True)
class AuthenticationCommand(InitiationCommand):
    @classmethod
    def get_identifier(cls) -> str:
        return 'AUTHENTICATION'

    def invoke(self, receiver: AuthenticationReceiver) -> List[Command]:
        agent: Agent = self.initiation_context.agent
        if not agent.send_socket:
            auth_command = AuthenticationCommand()
            broker: Broker = InstanceContainer.resolve(Broker)
            payload = Payload(auth_command, ConnectionSettings(agent.address, TorConfiguration.get_tor_server_port()))
            broker.send(payload)
