from queue import Queue
from threading import Thread
from time import sleep
from typing import Iterable
from dataclasses import dataclass

from app.messaging.commands import CommandMapper, Command
from app.messaging.command_handler import BaseCommandHandler
from app.networking.tor import PacketHandler, TorClient
from app.networking.base import Packet, ConnectionSettings


@dataclass(frozen=True)
class Payload:
    '''Command + information where to send it.'''
    command: Command
    address: ConnectionSettings


class Broker(PacketHandler, Thread):
    def __init__(self, command_mapper: CommandMapper, command_handler: BaseCommandHandler):
        super().__init__()
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._command_mapper = command_mapper
        self._command_handler = command_handler

    def run(self):
        while True:
            self._handle_incoming()
            self._handle_outgoing()
            sleep(0.01)

    def handle(self, packet: Packet):
        payload = Payload(self._command_mapper.map_from_bytes(packet.data), packet.address)
        self._recv_queue.put(payload)

    def send(self, payload: Payload):
        self._send_queue.put(payload)

    def _handle_outgoing(self):
        while self._send_queue.not_empty:
            payload = self._send_queue.get()
            packet = Packet(self._command_mapper.map_to_bytes(payload.command), payload.address)
            client = TorClient(packet)
            client.start()

    def _handle_incoming(self):
        while self._recv_queue.not_empty:
            payload: Payload = self._recv_queue.get()
            command, address = payload.command, payload.address
            responses: Iterable[Command] = self._command_handler.handle(command)
            for response in responses:
                response_payload = Payload(response, address)
                self.send(response_payload)