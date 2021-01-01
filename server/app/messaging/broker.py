import logging
from app.api.commands import HelloCommand
from app.messaging.messaging_commands import AuthenticationCommand
from app.networking.topology import Agent, Topology
from app.networking.authentication import Authentication
from queue import Queue
from time import sleep
from typing import Iterable
from dataclasses import dataclass

from app.messaging.base import CommandMapper, Command
from app.messaging.command_handler import BaseCommandHandler
from app.networking.tor import TorConnection, TorConnectionFactory
from app.networking.base import ConnectionSettings, Packet, PacketHandler
from app.shared.config import TorConfiguration
from app.shared.multithreading import StoppableThread


@dataclass(frozen=True)
class Payload:
    command: Command
    address: ConnectionSettings


class Broker(StoppableThread, PacketHandler, Authentication):
    def __init__(self, command_mapper: CommandMapper, command_handler: BaseCommandHandler, topology: Topology):
        super().__init__()
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._command_mapper = command_mapper
        self._command_handler = command_handler
        self._topology = topology
        self._tor_connection_factory = TorConnectionFactory(topology)
        self._logger = logging.getLogger(__name__)

    def run(self):
        while True:
            self._handle_incoming()
            self._handle_outgoing()
            sleep(0.01)

    def handle(self, packet: Packet):
        payload = Payload(self._command_mapper.map_from_bytes(packet.data), packet.address)
        self._recv_queue.put(payload)
        self._logger.info(f'Queued: {payload.command.__class__.__name__} received from {payload.address}')

    def send(self, payload: Payload):
        self._send_queue.put(payload)
        self._logger.info(f'Queued: {payload.command.__class__.__name__} sent to {payload.address}')


    def authenticate(self, agent: Agent, first_packet: Packet):
        command = self._command_mapper.map_from_bytes(first_packet.data)
        if isinstance(command, AuthenticationCommand):
            agent.address = command.source
            self._logger.info(f'Authenticated {command.source}')
            # some form of authentication
        elif isinstance(command, HelloCommand):
            command.helloContext.initialize(agent)
            payload = Payload(command, ConnectionSettings(command.source, TorConfiguration.get_tor_server_port()))
            self._recv_queue.put(payload)
            self._logger.info(f'Queued: HelloCommand received from {command.source}')
            self._topology.remove_by_socket(agent.socket)

    def _handle_outgoing(self):
        while not self._send_queue.empty():
            payload: Payload = self._send_queue.get()
            packet = Packet(self._command_mapper.map_to_bytes(payload.command), payload.address)
            connection = self._tor_connection_factory.get_connection(payload.address.address)
            connection.send(packet)

    def _handle_incoming(self):
        while not self._recv_queue.empty():
            payload: Payload = self._recv_queue.get()
            command, address = payload.command, payload.address
            command.context.initialize(payload.address)
            responses: Iterable[Command] = self._command_handler.handle(command)
            for response in responses:
                response_payload = Payload(response, address)
                self.send(response_payload)