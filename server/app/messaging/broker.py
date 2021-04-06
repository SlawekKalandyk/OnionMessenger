from abc import ABC, abstractmethod
from app.shared.config import TorConfiguration
from app.messaging.messaging_commands import ImAliveCommand, SingleUseCommand
import logging
from app.networking.topology import Topology
from queue import Queue
from time import sleep, time
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


class ConnectionFailureCallback(ABC):
    @abstractmethod
    def on_connection_failure(self, address: str):
        pass


class Broker(StoppableThread, PacketHandler):
    def __init__(self, command_mapper: CommandMapper, command_handler: BaseCommandHandler, topology: Topology, connection_failure_callback: ConnectionFailureCallback = None):
        super().__init__()
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._command_mapper = command_mapper
        self._command_handler = command_handler
        self._topology = topology
        self._tor_connection_factory = TorConnectionFactory(topology)
        self._connection_failure_callback = connection_failure_callback
        self._imalive_interval = 45
        self._logger = logging.getLogger(__name__)

    def run(self):
        while True:
            self._handle_incoming()
            self._handle_outgoing()
            self._handle_imalive()
            sleep(0.1)

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
                if isinstance(payload.command, SingleUseCommand):
                    agent = self._topology.get_by_address(payload.address.address)
                    self._topology.remove(agent)
                    agent.close_sockets()
            else:
                if self._connection_failure_callback:
                    self._connection_failure_callback.on_connection_failure(payload.address.address)

    def _handle_incoming(self):
        while not self._recv_queue.empty():
            payload: Payload = self._recv_queue.get()
            command, address = payload.command, payload.address
            command.context.initialize(payload.address)
            responses: Iterable[Command] = self._command_handler.handle(command)
            for response in responses:
                response_payload = Payload(response, address)
                self.send(response_payload)

    def _handle_imalive(self):
        current_time = time()
        for agent in self._topology.get_all_active_agents():
            if current_time - agent.last_contact_time > self._imalive_interval:
                imalive = ImAliveCommand()
                connection_settings = ConnectionSettings(agent.address, TorConfiguration.get_tor_server_port())
                payload = Payload(imalive, connection_settings)
                self.send(payload)
        # TODO: close inactive agents
        # May not be needed, if ImAlive (or any command really) gets a ConnectionAbortedError
        # the connection is shut down