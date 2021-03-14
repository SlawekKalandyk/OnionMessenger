from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from socket import socket
from typing import List


@dataclass(frozen=False)
class Agent():
    address: str = ""
    send_socket: socket = None
    receive_socket: socket = None
    time_since_last_contact: float = -1

    def merge(self, agent: Agent):
        if not self.address:
            self.address = agent.address
        if not self.send_socket:
            self.send_socket = agent.send_socket
        if not self.receive_socket:
            self.receive_socket = agent.receive_socket

    def close_sockets(self):
        if self.send_socket:
            self.send_socket.close()
        if self.receive_socket:
            self.receive_socket.close()


class AgentRemoveCallback(ABC):
    @abstractmethod
    def on_agent_removed(self, agent: Agent):
        pass


class Topology():
    def __init__(self, agent_removal_callback: AgentRemoveCallback = None) -> None:
        self._agents = []
        self._logger = logging.getLogger(__name__)
        self._removal_callback = agent_removal_callback

    def append(self, agent: Agent):
        self._agents.append(agent)
        self._logger.info(f'Agent {agent.address} added to topology')

    def remove(self, agent: Agent):
        try:
            self._agents.remove(agent)
        except ValueError:
            self._logger.error(f'Agent {agent} cannot be removed from topology, he already wasn\'t there')
        else:
            if self._removal_callback:
                self._removal_callback.on_agent_removed(agent)
            self._logger.info(f'Agent {agent.address} removed from topology')

    def remove_by_socket(self, sock: socket):
        agent = self.get_by_socket(sock)
        if agent:
            self.remove(agent)
        else:
            self._logger.error(f'Agent for socket {sock} was not found, cannot be removed')

    def remove_by_address(self, address: str):
        agent = self.get_by_address(address)
        self.remove(agent)
        
    def get_all_sockets(self) -> List[socket]:
        return self.get_all_send_sockets().extend(self.get_all_receive_sockets())

    def get_by_socket(self, sock: socket) -> Agent:
        agents = list(filter(lambda x: sock and (x.send_socket is sock or x.receive_socket is sock), self._agents))
        return agents[0] if agents else None

    def get_by_address(self, address: str) -> Agent:
        agents = list(filter(lambda x: x.address == address and address != '', self._agents))
        return agents[0] if agents else None

    def get_all_nonempty_addresses(self):
        addresses_only = list(map(lambda x: x.address, self._agents))
        nonempty_addresses = list(filter(lambda x: x != "", addresses_only))
        return nonempty_addresses

    def get_all_send_sockets(self):
        all_send_sockets =  list(map(lambda x: x.send_socket, self._agents))
        return list(filter(lambda x: x, all_send_sockets))

    def get_all_receive_sockets(self):
        all_receive_sockets =  list(map(lambda x: x.receive_socket, self._agents))
        return list(filter(lambda x: x, all_receive_sockets))
        