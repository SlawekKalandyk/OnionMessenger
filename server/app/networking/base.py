from abc import abstractmethod, ABC
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
from socketserver import ThreadingTCPServer

@dataclass_json
@dataclass(frozen=True)
class ConnectionSettings:
    address: str
    port: int

    @staticmethod
    def from_tuple(address_info: tuple):
        return ConnectionSettings(address_info[0], address_info[1])

    def to_tuple(self) -> tuple:
        return (self.address, self.port)


@dataclass(frozen=True)
class Packet:
    data: bytes
    address: ConnectionSettings


class PacketHandler(ABC):
    @abstractmethod
    def handle_packet(self, packet: Packet):
        pass


class HandleableThreadingTCPServer(ThreadingTCPServer):
    def __init__(self, address, requestHandler, packetHandler):
        super().__init__(address, requestHandler)
        self._packet_handler = packetHandler


class HiddenServiceStartObserver(ABC):
    @abstractmethod
    def update(self):
        pass