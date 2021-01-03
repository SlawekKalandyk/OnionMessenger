from app.messaging.broker import Broker, Payload
from app.api.commands import HelloCommand
from app.shared.config import TorConfiguration
from app.messaging.messaging_commands import AuthenticationCommand, InitiationCommand
from app.networking.topology import Agent, Topology
from app.networking.base import ConnectionSettings, Packet, PacketHandler
from app.networking.authentication import Authentication
from app.messaging.base import CommandMapper
from app.messaging.command_handler import BaseCommandHandler


class Authenticator(Authentication):
    def __init__(self, command_mapper: CommandMapper, command_handler: BaseCommandHandler, broker: Broker, topology: Topology):
        self._command_mapper = command_mapper
        self._command_handler = command_handler
        self._broker = broker
        self._topology = topology

    def authenticate(self, agent: Agent, first_packet: Packet):
        command = self._command_mapper.map_from_bytes(first_packet.data)
        # if an agent for this address already exists, merge him with the new one
        probable_agent = self._topology.get_by_address(command.source)
        if probable_agent:
            probable_agent.merge(agent)
            self._topology.remove(agent)
            agent = probable_agent
        
        if isinstance(command, InitiationCommand):
            if isinstance(command, AuthenticationCommand):
                agent.address = command.source

            command.initiation_context.initialize(agent)
            payload = Payload(command, ConnectionSettings(command.source, TorConfiguration.get_tor_server_port()))
            self._broker.handle_payload(payload)

            if isinstance(command, HelloCommand):
                self._topology.remove(agent)