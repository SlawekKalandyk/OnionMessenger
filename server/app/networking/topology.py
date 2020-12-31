from dataclasses import dataclass
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

    def append(self, agent: Agent):
        self._agents.append(agent)

    def get_all_sockets(self) -> List[socket]:
        return list(map(lambda x: x.socket, self._agents))

    def remove_by_socket(self, sock: socket):
        agent = self.get_by_socket(sock)
        self._agents.remove(agent)

    def get_by_socket(self, sock: socket):
        agent = list(filter(lambda x: x.socket is sock), self._agents)[0]
        return agent

    def get_all_nonempty_addresses(self):
        addresses_only = list(map(lambda x: x.address, self._agents))
        nonempty_addresses = list(filter(lambda x: x != "", addresses_only))
        return nonempty_addresses
        