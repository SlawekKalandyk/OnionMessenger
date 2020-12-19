from app.networking.tor import TorClient, TorServer, TorService
from app.networking.base import ConnectionSettings
from app.messaging.commands import CommandMapper
from app.messaging.command_handler import CommandHandler
from app.messaging.broker import Broker
from app.shared.container import InstanceContainer
from app.api.endpoints import flaskapp, socketIO
from flask_socketio import SocketIO

def main():
    # server_settings = ConnectionSettings('127.0.0.1', 39124)
    # command_mapper = CommandMapper()
    # command_handler = CommandHandler(command_mapper)
    # broker = Broker(command_mapper, command_handler)
    # broker.start()
    # tor_server = TorServer(server_settings, broker)
    # tor_server.start()
    # tor_service = TorService(server_settings)
    # tor_service.start()
    
    # InstanceContainer.register_singleton(Broker, broker)
    # InstanceContainer.register_singleton(TorServer, tor_server)
    # InstanceContainer.register_singleton(TorService, tor_service)
    InstanceContainer.register_singleton(SocketIO, socketIO)
    
    socketIO.run(flaskapp)

if __name__ == '__main__':
    main()