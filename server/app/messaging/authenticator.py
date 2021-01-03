import logging
from app.api.commands import HelloCommand
from app.shared.config import TorConfiguration
from app.messaging.messaging_commands import AuthenticationCommand, InitiationCommand
from app.networking.topology import Agent, Topology
from app.networking.base import ConnectionSettings, Packet, PacketHandler
from app.networking.authentication import Authentication
from app.messaging.base import CommandMapper
from app.messaging.command_handler import BaseCommandHandler


class Authenticator(Authentication):
    def __init__(self, command_mapper: CommandMapper, command_handler: BaseCommandHandler, packet_handler: PacketHandler, topology: Topology):
        self._command_mapper = command_mapper
        self._command_handler = command_handler
        self._packet_handler = packet_handler
        self._topology = topology
        self._logger = logging.getLogger(__name__)

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
                
            packet = Packet(first_packet.data, ConnectionSettings(command.source, TorConfiguration.get_tor_server_port()))
            self._packet_handler.handle(packet)

            if isinstance(command, HelloCommand):
                self._topology.remove(agent)

            self._logger.info(f'Queued: {command.__class__.__name__} received from {command.source}')