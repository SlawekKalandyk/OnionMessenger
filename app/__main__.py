from app.networking.tor import TorClient, TorServer, TorService
from app.networking.base import ConnectionSettings
from time import sleep

if __name__ == '__main__':
    server_settings = ConnectionSettings('127.0.0.1', 39123)
    
    tor_server = TorServer(server_settings)
    tor_server.start()
    tor_service = TorService(server_settings)
    tor_service.start()