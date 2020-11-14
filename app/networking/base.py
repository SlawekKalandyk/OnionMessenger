from abc import abstractmethod, ABC
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


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


class NetworkIO(ABC):
    @abstractmethod
    def send(self, packet: Packet):
        pass

    @abstractmethod
    def receive(self) -> Optional[Packet]:
        pass

    @abstractmethod
    def get_address(self) -> ConnectionSettings:
        pass