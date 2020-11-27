from app.networking.tor import TorClient, TorServer, TorService
from app.networking.base import ConnectionSettings
from app.messaging.commands import CommandMapper
from app.messaging.command_handler import CommandHandler
from app.messaging.broker import Broker

if __name__ == '__main__':
    server_settings = ConnectionSettings('127.0.0.1', 39123)
    command_mapper = CommandMapper()
    command_handler = CommandHandler()
    broker = Broker(command_mapper, command_handler)
    tor_server = TorServer(server_settings, broker)
    tor_server.start()
    tor_service = TorService(server_settings)
    tor_service.start()