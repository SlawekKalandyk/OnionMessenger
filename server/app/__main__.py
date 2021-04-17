from app.api.event_handlers import BacklogHandler
from app.messaging.messaging_commands import ImAliveCommand
from app.messaging.messaging_receivers import ImAliveCommandReceiver
from app.messaging.authenticator import Authenticator
from app.shared.logging import initialize_logging
from app.networking.topology import Topology
from app.api.observers import OfflineEmitterAgentRemoveCallback, OfflineEmitterConnectionFailureCallback, TorHiddenServiceStartObserver
from app.infrastructure.message import MessageRepository
from app.infrastructure.contact import ContactRepository
from app.api.receivers import ApproveCommandReceiver, AuthenticationReceiver, ConnectionEstablishedReceiver, HelloCommandReceiver, MessageCommandReceiver
from app.networking.tor import TorServer, TorService
from app.networking.base import ConnectionSettings
from app.api.commands import ApproveCommand, AuthenticationCommand, ConnectionEstablishedCommand, HelloCommand, MessageCommand
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
    command_mapper.register(ImAliveCommand)
    command_mapper.register(ConnectionEstablishedCommand)
    

def register_commands(command_handler: CommandHandler, topology: Topology):
    message_receiver = MessageCommandReceiver(ContactRepository(), MessageRepository())
    command_handler.register(MessageCommand, message_receiver)
    hello_receiver = HelloCommandReceiver(ContactRepository(), topology)
    command_handler.register(HelloCommand, hello_receiver)
    approve_receiver = ApproveCommandReceiver(ContactRepository(), topology)
    command_handler.register(ApproveCommand, approve_receiver)
    authentication_receiver = AuthenticationReceiver(ContactRepository(), topology)
    command_handler.register(AuthenticationCommand, authentication_receiver)
    im_alive_receiver = ImAliveCommandReceiver(topology)
    command_handler.register(ImAliveCommand, im_alive_receiver)
    connection_established_receiver = ConnectionEstablishedReceiver(ContactRepository(), topology)
    command_handler.register(ConnectionEstablishedCommand, connection_established_receiver)

def main():
    initialize_logging()

    server_settings = ConnectionSettings('127.0.0.1', 39124)

    command_mapper = CommandMapper()
    command_handler = CommandHandler(command_mapper)
    topology = Topology(OfflineEmitterAgentRemoveCallback())
    broker = Broker(command_mapper, command_handler, topology, OfflineEmitterConnectionFailureCallback())
    authenticator = Authenticator(command_mapper, command_handler, broker, topology)
    tor_server = TorServer(server_settings, broker, topology, authenticator)
    tor_service = TorService(server_settings)
    tor_service.add_hidden_service_start_observer(TorHiddenServiceStartObserver())
    
    InstanceContainer.register_singleton(Topology, topology)
    InstanceContainer.register_singleton(Broker, broker)
    InstanceContainer.register_singleton(TorServer, tor_server)
    InstanceContainer.register_singleton(TorService, tor_service)
    InstanceContainer.register_singleton(SocketIO, socketIO)

    register_command_mappings(command_mapper)
    register_commands(command_handler, topology)
    broker.loop_event += BacklogHandler().handle_backlog

    InstanceContainer.register_singleton(CommandMapper, command_mapper)

    broker.start()
    tor_server.start()
    tor_service.start()
    socketIO.run(flaskapp)

if __name__ == '__main__':
    main()