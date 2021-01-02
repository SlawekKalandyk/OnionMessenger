from dataclasses import dataclass
import logging
from socket import socket
from typing import List


@dataclass(frozen=False)
class Agent():
    address: str = ""
    socket: socket = None
    time_since_last_contact: float = -1


class Topology():
    def __init__(self) -> None:
        self._agents = []
        self._logger = logging.getLogger(__name__)

    def append(self, agent: Agent):
        self._agents.append(agent)
        self._logger.info(f'Agent {agent.address} added to topology')

    def get_all_sockets(self) -> List[socket]:
        return list(map(lambda x: x.socket, self._agents))

    def remove_by_socket(self, sock: socket):
        agent = self.get_by_socket(sock)
        self._agents.remove(agent)
        self._logger.info(f'Socket for {agent.address} removed from topology')

    def get_by_socket(self, sock: socket) -> Agent:
        agent = list(filter(lambda x: x.socket is sock, self._agents))[0]
        return agent

    def get_by_address(self, address: str) -> Agent:
        agent = list(filter(lambda x: x.address == address and address != '', self._agents))[0]
        return agent

    def get_all_nonempty_addresses(self):
        addresses_only = list(map(lambda x: x.address, self._agents))
        nonempty_addresses = list(filter(lambda x: x != "", addresses_only))
        return nonempty_addresses
        