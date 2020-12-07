from app.networking.tor import TorClient, TorServer, TorService
from app.networking.base import ConnectionSettings
from app.messaging.commands import CommandMapper
from app.messaging.command_handler import CommandHandler
from app.messaging.broker import Broker
from app.api.endpoints import app


if __name__ == '__main__':
    # server_settings = ConnectionSettings('127.0.0.1', 39122)
    # command_mapper = CommandMapper()
    # command_mapper.register(TestCommand)
    # command_handler = CommandHandler(command_mapper)
    # command_handler.register(TestCommand, 1)
    # broker = Broker(command_mapper, command_handler)
    # broker.start()
    # tor_server = TorServer(server_settings, broker)
    # tor_server.start()
    # tor_service = TorService(server_settings)
    # tor_service.start()
    app.run(debug=True)