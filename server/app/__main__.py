from app.api.event_handlers import BacklogHandler, on_agent_removed, on_connection_failure, on_hidden_service_start
from app.messaging.messaging_commands import ImAliveCommand
from app.messaging.authenticator import Authenticator
from app.shared.logging import initialize_logging
from app.networking.topology import Topology
from app.infrastructure.message import MessageRepository
from app.infrastructure.contact import ContactRepository
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


def main():
    initialize_logging()

    server_settings = ConnectionSettings('127.0.0.1', 39124)

    command_mapper = CommandMapper()
    command_handler = CommandHandler()
    topology = Topology()
    broker = Broker(command_mapper, command_handler, topology)
    authenticator = Authenticator(command_mapper, command_handler, broker, topology)
    tor_server = TorServer(server_settings, broker, topology, authenticator)
    tor_service = TorService(server_settings)
    
    InstanceContainer.register_singleton(CommandMapper, command_mapper)
    InstanceContainer.register_singleton(Topology, topology)
    InstanceContainer.register_singleton(Broker, broker)
    InstanceContainer.register_singleton(TorServer, tor_server)
    InstanceContainer.register_singleton(TorService, tor_service)
    InstanceContainer.register_singleton(SocketIO, socketIO)

    register_command_mappings(command_mapper)
    topology.agent_removed_event += on_agent_removed
    tor_service.hidden_service_start_event += on_hidden_service_start
    broker.connection_failure_event += on_connection_failure
    broker.loop_event += BacklogHandler().handle_backlog

    broker.start()
    tor_server.start()
    tor_service.start()
    socketIO.run(flaskapp)

if __name__ == '__main__':
    main()