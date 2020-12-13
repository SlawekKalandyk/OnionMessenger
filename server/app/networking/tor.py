from stem import control
from stem.process import launch_tor_with_config
from stem.process import subprocess
from stem.control import Controller
import socket
import socks
from threading import Thread
import socketserver
from abc import ABC, abstractmethod

from app.networking.base import ConnectionSettings, Packet, PacketHandler, HandleableThreadingTCPServer
from app.shared.helpful_abstractions import Closable
from app.shared.config import TorConfiguration
from app.shared.multithreading import StoppableThread


class TorServer(StoppableThread, Closable):
    def __init__(self, connection_settings: ConnectionSettings, handler: PacketHandler):
        super().__init__()
        self._connection_settings = connection_settings
        self._tcp_server: socketserver.ThreadingTCPServer = HandleableThreadingTCPServer(self._connection_settings.to_tuple(), TorRequestHandler, handler)

    def run(self):
        server_thread = Thread(target=self._tcp_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
    def close(self):
        self._tcp_server.shutdown()


class TorClient(StoppableThread, Closable):
    def __init__(self, packet: Packet):
        super().__init__()
        self._packet = packet
        self._socket = self._create_socket()

    def run(self):
        self._connect()
        self.send()
        self.close()

    def close(self):
        self._socket.close()

    def send(self):
        self._socket.send(self._packet.data)

    def _create_socket(self) -> socket.socket:
        socket.socket = socks.socksocket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.set_proxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
        return s

    def _connect(self):
        self._socket.connect(self._packet.address.to_tuple())


class TorService(StoppableThread, Closable):
    def __init__(self, connection_settings: ConnectionSettings):
        super().__init__()
        self._connection_settings = connection_settings
        self._controller: Controller = None
        self._tor: subprocess.Popen = None

    def run(self):
        self._start_hidden_service()

    def close(self):
        if self._controller != None:
            self._controller.close()
        if self._tor != None:
            self._tor.terminate()

    def _start_hidden_service(self):
        self._tor = launch_tor_with_config(tor_cmd=TorConfiguration.get_tor_executable_path(), config = {
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
            
        print('Service established at %s.onion' % response.service_id)


class TorRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        handler = self.server._packet_handler
        connection, address = self.request, self.client_address
        # TODO: make it handle any size received
        data = connection.recv(65536)
        handler.handle(Packet(data, ConnectionSettings.from_tuple(address)))