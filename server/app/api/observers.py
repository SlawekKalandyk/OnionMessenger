from app.shared.config import TorConfiguration
from app.messaging.broker import Broker, Payload
from app.shared.container import InstanceContainer
from app.messaging.messaging_commands import AuthenticationCommand
from app.infrastructure.contact import ContactRepository
from app.api.socket_emitter import emit_service_start
from app.networking.base import ConnectionSettings, HiddenServiceStartObserver

class TorHiddenServiceStartObserver(HiddenServiceStartObserver):
    def update(self):
        emit_service_start()
        repository = ContactRepository()
        approved_addresses = list(map(lambda x: x.address, repository.get_all_approved()))
        broker: Broker = InstanceContainer.resolve(Broker)
        for address in approved_addresses:
            auth_command = AuthenticationCommand()
            payload = Payload(auth_command, ConnectionSettings(address, TorConfiguration.get_tor_server_port()))
            broker.send(payload)
