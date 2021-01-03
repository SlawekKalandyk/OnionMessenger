from abc import ABC, abstractmethod
from app.networking.topology import Agent
from app.networking.base import Packet

class Authentication(ABC):
    @abstractmethod
    def authenticate(self, agent: Agent, first_packet: Packet):
        pass