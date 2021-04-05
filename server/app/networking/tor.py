from re import search
from app.shared.utility import stem_compatible_base64_blob_from_private_key
from app.shared.signature import Signature
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
from app.shared.config import PacketConfiguration, TorConfiguration
from app.shared.multithreading import StoppableThread


class TorServer(StoppableThread, Closable):
    def __init__(self, connection_settings: ConnectionSettings, handler: PacketHandler, topology: Topology, authentication: Authentication):
        super().__init__()
        socket.socket = socks.socksocket
        self._connection_settings = connection_settings
        self._packet_handler = handler
        self._topology = topology
        self._authentication = authentication
        self._socket = self._setup_server_socket()
        self._logger = logging.getLogger(__name__)
        
    def run(self):
        self._socket.listen()

        while True:
            readers = self._topology.get_all_receive_sockets()
            writers = self._topology.get_all_send_sockets()
            readers.append(self._socket)
            errors = readers + writers

            read, _, err = select.select(readers, writers, errors)

            for sock in read:
                if sock is self._socket:
                    # accept socket as non-blocking, ignore client_address since in this case it contains no peer data
                    client_socket, _ = self._socket.accept()
                    client_socket.setblocking(0)
                    # even if an agent for this socket already exists, put it in topology for now
                    self._topology.append(Agent(receive_socket=client_socket, time_since_last_contact=0))
                else:
                    # if file descriptor is -1, it means the socket has been closed
                    if sock.fileno() == -1:
                        agent = self._topology.get_by_socket(sock)
                        if agent:
                            self._topology.remove(agent)
                            agent.close_sockets()
                        continue
                            
                    data = self._receive_all(sock)
                    agent = self._topology.get_by_socket(sock)
                    if data:
                        # if sock in topology has empty address:
                        #   handle first contact - command HAS to contain source address
                        if agent.address == "":
                            packet = Packet(data)
                            self._authentication.authenticate(agent, packet)
                        else:
                            packet = Packet(data, ConnectionSettings(agent.address, TorConfiguration.get_tor_server_port()))
                            self._packet_handler.handle(packet)
                    else:
                        # if received data length is 0, it means the socket has been closed on the other side
                        self._logger.info(f'Disconnected from {agent.address}')
                        self._topology.remove(agent)
                        agent.close_sockets()
            for sock in err:
                self._logger.error(f'Error in {sock}')
                self._topology.get_by_socket(sock).close_sockets()
                self._topology.remove_by_socket(sock)
        
    def close(self):
        pass

    def _setup_server_socket(self):
        socket.socket = socks.socksocket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setblocking(0)
        server_socket.bind(self._connection_settings.to_tuple())

        return server_socket


    def _receive_all(self, sock: socket.socket) -> bytes:
        """
        Receive all data sent by socket.
        The structure is <size>:<data> with size being an int.
        """
        batch_size = PacketConfiguration.packet_batch_size
        # packet size length + ':' symbol
        first_data = sock.recv(PacketConfiguration.packet_size_info_limit + 1)
        first_data_str = first_data.decode('utf-8')
        index = search(r':', first_data_str).start()
        size, first_data_without_size = int(first_data_str[:index]), first_data[(index + 1):]
        first_data_without_size = first_data[(index + 1):] if index < PacketConfiguration.packet_size_info_limit else []

        if size > PacketConfiguration.packet_size_limit:
            raise PacketSizeOverLimitError(size)

        total_data = first_data_without_size
        while len(total_data) < size:
            total_data += sock.recv(batch_size)

        return total_data


class PacketSizeOverLimitError(Exception):
    pass


class TorConnection():
    def __init__(self, sock: socket.socket):
        self._socket = sock
        self._logger = logging.getLogger(__name__)

    def send(self, packet: Packet):
        """
        Send packet to selected socket. Before sending, '<size>:' is prepended to packet's data.
        """
        size = len(packet.data)
        data = (str(size) + ':').encode('utf-8')
        data = data + packet.data
        self._socket.send(data)


class TorConnectionFactory():
    def __init__(self, topology: Topology):
        self._topology = topology
        self._logger = logging.getLogger(__name__)

    def get_outgoing_connection(self, address: str):
        # check if agent exists, then if send_socket exists return connection
        agent = self._topology.get_by_address(address)
        if agent and agent.send_socket:
            return ActionResult(TorConnection(agent.send_socket), True)

        # if we're here then socket doesn't exist
        sock = self._create_socket()
        try:
            sock.connect((address, TorConfiguration.get_tor_server_port()))
        except socks.GeneralProxyError as err:
            self._logger.error(f'Could not connect to {address}')
            return ActionResult(None, False)
        else:
            # if agent exists set his send_socket, if not create a new agent
            if agent:
                agent.send_socket = sock
            else:
                agent = Agent(address=address, send_socket=sock, time_since_last_contact=0.0)
                self._topology.append(agent)
            return ActionResult(TorConnection(agent.send_socket), True)

    def _create_socket(self) -> socket.socket:
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
        private_key = TorConfiguration.get_hidden_service_private_key()
        is_new_user = private_key == None
        if is_new_user:
            private_key, public_key = Signature.generate_keys()
            TorConfiguration.save_hidden_service_private_key(private_key)
            TorConfiguration.save_hidden_service_public_key(public_key)

        key_content = stem_compatible_base64_blob_from_private_key(private_key)
        response = self._controller.create_ephemeral_hidden_service(ports={TorConfiguration.get_tor_server_port(): self._connection_settings.port}, await_publication=True, \
            key_type='ED25519-V3', key_content=key_content)
            
        if is_new_user:
            TorConfiguration.save_hidden_service_id(response.service_id)
            
        self._logger.info(f'Service established at {response.service_id}.onion')
        self._notify_hidden_service_start_observers()