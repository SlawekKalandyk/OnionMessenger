from threading import Thread
from app.shared.event import Event
from app.shared.config import TorConfiguration
from app.messaging.messaging_commands import ImAliveCommand, SaveableCommand
import logging
from app.networking.topology import Topology
from queue import Queue
from time import sleep, time
from typing import Iterable
from dataclasses import dataclass
from app.messaging.base import CommandMapper, Command, CommandTypeNotRegisteredError
from app.messaging.command_handler import BaseCommandHandler
from app.networking.tor import TorConnection, TorConnectionFactory
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
        self._imalive_interval = 30
        self.service_started = False
        self.connection_failure_event = Event()
        self.loop_event = Event()
        self._logger = logging.getLogger(__name__)

    def run(self):
        while True:
            if self.service_started:
                self._handle_incoming()
                self._handle_outgoing()
                self._handle_imalive()
                self.loop_event.notify(self)
            sleep(0.1)

    def handle(self, packet: Packet):
        try:
            payload = Payload(self._command_mapper.map_from_bytes(packet.data), packet.address)
        except CommandTypeNotRegisteredError:
            self._logger.error(f'Packet received from {packet.address.address} contains an unregistered command')
            return
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
                connection: TorConnection = connection_action_result.value
                # if send fails, save command
                if isinstance(payload.command, SaveableCommand):
                    connection.failed_to_send_event += payload.command.save
                connection.before_sending_event += payload.command.before_sending
                connection.after_sending_event += payload.command.after_sending
                connection_thread = Thread(target=connection.send, args=(packet,))
                connection_thread.start()
            else:
                # if connection couldn't be established, save command
                self.connection_failure_event.notify(payload.address.address)
                if isinstance(payload.command, SaveableCommand):
                    payload.command.save(payload.address.address)

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
