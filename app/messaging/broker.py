from queue import Queue

from app.messaging.commands import CommandMapper
from app.messaging.command_handler import CommandHandler
from app.networking.tor import PacketHandler
from app.networking.base import Packet


class Broker(PacketHandler):
    def __init__(self, command_mapper: CommandMapper, command_handler: CommandHandler):
        self._send_queue = Queue()
        self._recv_queue = Queue()
        self._command_mapper = command_mapper
        self._command_handler = command_handler

    def handle(self, packet: Packet):
        pass