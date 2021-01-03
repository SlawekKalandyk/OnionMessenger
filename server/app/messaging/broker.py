import logging
from app.networking.topology import Topology
from queue import Queue
from time import sleep
from typing import Iterable
from dataclasses import dataclass

from app.messaging.base import CommandMapper, Command
from app.messaging.command_handler import BaseCommandHandler
from app.networking.tor import TorConnectionFactory
from app.networking.base import ConnectionSettings, Packet, PacketHandler
from app.shared.multithreading import StoppableThread


@dataclass(frozen=True)
class Payload:
    command: Command
    address: ConnectionSettings


class Broker(StoppableThread, PacketHandler):
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
        self.handle_payload(payload)
    
    def handle_payload(self, payload: Payload):
        self._recv_queue.put(payload)
        self._logger.info(f'Queued: {payload.command.__class__.__name__} received from {payload.address}')

    def send(self, payload: Payload):
        self._send_queue.put(payload)
        self._logger.info(f'Queued: {payload.command.__class__.__name__} sent to {payload.address}')
            
    def _handle_outgoing(self):
        while not self._send_queue.empty():
            payload: Payload = self._send_queue.get()
            packet = Packet(self._command_mapper.map_to_bytes(payload.command), payload.address)
            connection_action_result = self._tor_connection_factory.get_outgoing_connection(payload.address.address)
            if connection_action_result.valid:
                connection_action_result.value.send(packet)

    def _handle_incoming(self):
        while not self._recv_queue.empty():
            payload: Payload = self._recv_queue.get()
            command, address = payload.command, payload.address
            command.context.initialize(payload.address)
            responses: Iterable[Command] = self._command_handler.handle(command)
            for response in responses:
                response_payload = Payload(response, address)
                self.send(response_payload)