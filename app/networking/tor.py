from stem import control
from stem.process import launch_tor_with_config
from stem.process import subprocess
from stem.control import Controller
import socket
import socks
from threading import Thread
import socketserver
from abc import ABC, abstractmethod

from app.networking.base import ConnectionSettings, NetworkIO, Packet
from app.shared.helpful_abstractions import Closable


class PacketHandler(ABC):
    @abstractmethod
    def handle(self, packet: Packet):
        pass


class TorServer(Thread, Closable):
    def __init__(self, connection_settings: ConnectionSettings, handler: PacketHandler):
        super().__init__()
        self._connection_settings = connection_settings
        self._handler = handler
        self._tcp_server: socketserver.ThreadingTCPServer = socketserver.ThreadingTCPServer(self._connection_settings.to_tuple(), TorRequestHandler)

    def run(self):
        server_thread = Thread(target=self._tcp_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
    def close(self):
        self._tcp_server.shutdown()

    def get_handler(self):
        return self._handler


class TorClient(Thread, Closable):
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
        self._socket.sendto(self._packet.data, self._packet.address.to_tuple())

    def _create_socket(self) -> socket.socket:
        socket.socket = socks.socksocket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.set_proxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
        return s

    def _connect(self):
        self._socket.connect(self._packet.address.to_tuple())


class TorService(Thread, Closable):
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
        self._tor = launch_tor_with_config(tor_cmd='D:\\Programming\\tor-win32-0.4.4.5\\Tor\\tor.exe', config = {
            'ControlPort': '9051'
        })
        self._controller = Controller.from_port()
        self._controller.authenticate()
        response = self._controller.create_ephemeral_hidden_service(ports={39123: self._connection_settings.port}, await_publication=True, \
            key_type='ED25519-V3', key_content='ELvn4pIOL/kjVKF3e8lNxv8dU/XTam/9t3y+Ipq7+0d79Cepd/vzro7W5P1CqYtCVaD9iNTifzVIjfSqo+GyUw==')
        print('Service established at %s.onion' % response.service_id)


class TorRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        handler = self.server.get_handler()
        connection, address = self.request, self.client_address
        # TODO: make it handle any size received
        data = connection.recv(65536)
        handler.handle(Packet(data, ConnectionSettings.from_tuple(address)))