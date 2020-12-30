from app.messaging.messaging_receivers import AuthenticationReceiver
from app.messaging.messaging_commands import AuthenticationCommand
from app.networking.topology import Topology
from app.api.observers import TorHiddenServiceStartObserver
from app.infrastructure.message import MessageRepository
from app.infrastructure.contact import ContactRepository
from app.api.receivers import ApproveCommandReceiver, HelloCommandReceiver, MessageCommandReceiver
from app.networking.tor import TorServer, TorService
from app.networking.base import ConnectionSettings
from app.api.commands import ApproveCommand, HelloCommand, MessageCommand
from app.messaging.base import CommandMapper
from app.messaging.command_handler import CommandHandler
from app.messaging.broker import Broker
from app.shared.container import InstanceContainer
from app.api.endpoints import flaskapp, socketIO
from flask_socketio import SocketIO

def register_command_mappings(command_mapper: CommandMapper):
    command_mapper.register(MessageCommand)
    command_mapper.register(HelloCommand)
    command_mapper.register(ApproveCommand)
    command_mapper.register(AuthenticationCommand)
    

def register_commands(command_handler: CommandHandler):
    message_receiver = MessageCommandReceiver(ContactRepository(), MessageRepository())
    command_handler.register(MessageCommand, message_receiver)
    hello_receiver = HelloCommandReceiver(ContactRepository())
    command_handler.register(HelloCommand, hello_receiver)
    approve_receiver = ApproveCommandReceiver(ContactRepository())
    command_handler.register(ApproveCommand, approve_receiver)
    authentication_receiver = AuthenticationReceiver()
    command_handler.register(AuthenticationCommand, authentication_receiver)


def main():
    server_settings = ConnectionSettings('127.0.0.1', 39124)
    command_mapper = CommandMapper()
    register_command_mappings(command_mapper)

    command_handler = CommandHandler(command_mapper)
    register_commands(command_handler)

    topology = Topology()
    InstanceContainer.register_singleton(Topology, topology)

    broker = Broker(command_mapper, command_handler, topology)
    broker.start()
    InstanceContainer.register_singleton(Broker, broker)

    tor_server = TorServer(server_settings, broker, topology, broker)
    tor_server.start()
    InstanceContainer.register_singleton(TorServer, tor_server)

    tor_service = TorService(server_settings)
    tor_service.add_hidden_service_start_observer(TorHiddenServiceStartObserver())
    tor_service.start()
    InstanceContainer.register_singleton(TorService, tor_service)
    
    InstanceContainer.register_singleton(SocketIO, socketIO)

    # set source for send in a different way than in endpoints (like take it from payload upon receival, may use CommandContext)
    
    socketIO.run(flaskapp)

if __name__ == '__main__':
    main()