from app.shared.action_result import ActionResult
import logging
from app.networking.authentication import Authentication
from app.networking.topology import Agent, Topology
from typing import List
from stem.process import launch_tor_with_config
from stem.process import subprocess
from stem.control import Controller
import socket
import socks
from time import sleep
import select

from app.networking.base import ConnectionSettings, HiddenServiceStartObserver, Packet, PacketHandler
from app.shared.helpful_abstractions import Closable
from app.shared.config import TorConfiguration
from app.shared.multithreading import StoppableThread


class TorServer(StoppableThread, Closable):
    def __init__(self, connection_settings: ConnectionSettings, handler: PacketHandler, topology: Topology, authentication: Authentication):
        super().__init__()
        self._connection_settings = connection_settings
        self._packet_handler = handler
        self._topology = topology
        self._authentication = authentication
        self._socket = self._setup_server_socket()
        self._logger = logging.getLogger(__name__)
        
    def run(self):
        self._socket.listen()

        while True:
            readers = self._topology.get_all_sockets()
            writers = self._topology.get_all_sockets()
            readers.append(self._socket)

            read, write, err = select.select(readers, writers, readers)

            for sock in read:
                self._logger.info(f'Incoming data from {sock.getpeername()}')
                if sock is self._socket:
                    client_socket, client_address = self._socket.accept()
                    self._logger.info(f'Client address: {client_address}')
                    client_socket.setblocking(0)
                    self._topology.append(Agent(socket=client_socket, time_since_last_contact=0))
                else:
                    data = sock.recv(2048)
                    decoded = data.decode('utf-8')
                    self._logger.info(f'Received {decoded}')
                    if data:
                        agent = self._topology.get_by_socket(sock)
                        # if sock in topology has empty address:
                        #   handle first contact - command HAS to contain source address
                        if agent.address == "":
                            packet = Packet(data)
                            self._authentication.authenticate(agent, packet)
                        else:
                            packet = Packet(data, ConnectionSettings(agent.address, TorConfiguration.get_tor_server_port()))
                            self._packet_handler.handle(packet)
                    else:
                        self._topology.remove_by_socket(sock)
                        sock.close()
            for sock in err:
                sock.close()
                self._topology.remove_by_socket(sock)
        
    def close(self):
        pass

    def _setup_server_socket(self):
        socket.socket = socks.socksocket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setblocking(0)
        server_socket.bind(self._connection_settings.to_tuple())

        return server_socket


class TorConnection():
    def __init__(self, socket: socket.socket):
        self._socket = socket
        self._logger = logging.getLogger(__name__)

    def send(self, packet: Packet):
        self._logger.info(f'Sending data to {packet.address} | {self._socket}')
        self._socket.send(packet.data)


class TorConnectionFactory():
    def __init__(self, topology: Topology):
        self._topology = topology
        self._logger = logging.getLogger(__name__)

    def get_connection(self, address: str):
        if address not in self._topology.get_all_nonempty_addresses():
            socket = self._create_socket()
            try:
                socket.connect((address, TorConfiguration.get_tor_server_port()))
            except socks.GeneralProxyError as err:
                self._logger.error(f'Could not connect to {address}')
                return ActionResult(None, False)
            else:
                self._topology.append(Agent(address=address, socket=socket, time_since_last_contact=0.0))
        else:
            socket = self._topology.get_by_address(address).socket
        return ActionResult(TorConnection(socket), True)

    def _create_socket(self) -> socks.socket:
        socket.socket = socks.socksocket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.set_proxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
        return s


class TorService(StoppableThread, Closable):
    def __init__(self, connection_settings: ConnectionSettings):
        super().__init__()
        self._connection_settings = connection_settings
        self._controller: Controller = None
        self._tor: subprocess.Popen = None
        self._hidden_service_start_observers: List(HiddenServiceStartObserver) = []
        self._logger = logging.getLogger(__name__)

    def run(self):
        self._start_hidden_service()
        # keep the thread alive indefinitely, so whenever it dies Tor dies with it
        while(True):
            sleep(0.1)

    def close(self):
        if self._controller != None:
            self._controller.close()
        if self._tor != None:
            self._tor.terminate()

    def add_hidden_service_start_observer(self, observer: HiddenServiceStartObserver):
        self._hidden_service_start_observers.append(observer)

    def _notify_hidden_service_start_observers(self):
        for observer in self._hidden_service_start_observers:
            observer.update()

    def _start_hidden_service(self):
        self._tor = launch_tor_with_config(tor_cmd=TorConfiguration.get_tor_executable_path(), take_ownership=True, config = {
            'ControlPort': '9051'
        })
        self._controller = Controller.from_port()
        self._controller.authenticate()
        key = TorConfiguration.get_hidden_service_key()
        key_type = 'ED25519-V3' if key else 'NEW'
        key_content = key if key else 'ED25519-V3'
        response = self._controller.create_ephemeral_hidden_service(ports={TorConfiguration.get_tor_server_port(): self._connection_settings.port}, await_publication=True, \
            key_type=key_type, key_content=key_content)
        if not key:
            TorConfiguration.save_hidden_service_key(response.private_key)
            TorConfiguration.save_hidden_service_id(response.service_id)
            
        self._logger.info(f'Service established at {response.service_id}.onion')
        self._notify_hidden_service_start_observers()