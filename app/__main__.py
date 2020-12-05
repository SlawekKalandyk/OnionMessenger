from app.networking.tor import TorClient, TorServer, TorService
from app.networking.base import ConnectionSettings
from app.messaging.commands import CommandMapper
from app.messaging.command_handler import CommandHandler
from app.messaging.broker import Broker

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from app.messaging.commands import Command
from app.infrastructure.message import ContentType
from typing import Any, List

@dataclass_json
@dataclass(frozen=True)
class TestCommand(Command):
    content: any
    content_type: ContentType

    @classmethod
    def get_identifier(cls) -> str:
        return 'TEST'

    def invoke(self, receiver: Any) -> List[Command]:
        print('Hello there')

if __name__ == '__main__':
    server_settings = ConnectionSettings('127.0.0.1', 39123)
    command_mapper = CommandMapper()
    command_mapper.register(TestCommand)
    command_handler = CommandHandler(command_mapper)
    command_handler.register(TestCommand, None)
    broker = Broker(command_mapper, command_handler)
    broker.start()
    tor_server = TorServer(server_settings, broker)
    tor_server.start()
    tor_service = TorService(server_settings)
    tor_service.start()