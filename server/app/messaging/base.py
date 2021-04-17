from app.networking.topology import Agent, Topology
from app.networking.base import ConnectionSettings
from dataclasses import dataclass, InitVar, field
from dataclasses_json import dataclass_json
from abc import ABC, abstractmethod
from typing import Dict, Tuple
from re import search

class Receiver(ABC):
    pass


@dataclass(frozen=False)
class CommandContext:
    sender: ConnectionSettings = None

    def initialize(self, sender: ConnectionSettings):
        self.sender = sender


@dataclass_json
@dataclass(frozen=True)
class Command(ABC):
    context: InitVar[CommandContext] = field(default=CommandContext(),
                                             init=False)
                                             
    @classmethod
    @abstractmethod
    def get_identifier(cls) -> str:
        pass

    @abstractmethod
    def invoke(self, receiver: Receiver):
        pass

    def _close_sockets(self, topology: Topology, agent: Agent):
        topology.remove(agent)
        agent.close_sockets()


class CommandMapper:
    def __init__(self):
        self._registered_commands: Dict[str, type] = dict()

    def register(self, command_type: type):
        identifier = command_type.get_identifier()
        self._registered_commands[identifier] = command_type
        return self

    def map_to_bytes(self, command: Command) -> bytes:
        return self.map_to_json(command).encode('utf-8')

    def map_from_bytes(self, data: bytes) -> Command:
        return self.map_from_json(data.decode('utf-8'))

    def map_to_json(self, command: Command) -> str:
        """
        Output in form IDENTIFIER{...}
        """
        self._assert_registered(command.get_identifier())
        code = command.to_json()
        return command.get_identifier() + code

    def map_from_json(self, data: str) -> Command:
        """
        Input in form IDENTIFIER{...}
        """
        identifier, code = self._parse(data)
        self._assert_registered(identifier)
        command_type = self._registered_commands[identifier]
        return command_type.from_json(code)

    def _parse(self, text: str) -> Tuple[str, str]:
        # find first non-alphanumeric character (should be '{')
        index = search(r'[^A-Z]', text).start()
        return text[:index], text[index:]

    def _assert_registered(self, identifier: str):
        if identifier not in self._registered_commands:
            raise CommandTypeNotRegisteredError(identifier)


class CommandTypeNotRegisteredError(Exception):
    pass