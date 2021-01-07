from app.networking.topology import Agent, AgentRemoveCallback
import logging
from app.shared.config import TorConfiguration
from app.messaging.broker import Broker, ConnectionFailureCallback, Payload
from app.shared.container import InstanceContainer
from app.infrastructure.contact import ContactRepository
from app.api.socket_emitter import emit_contact_offline, emit_service_start
from app.api.commands import AuthenticationCommand
from app.networking.base import ConnectionSettings, HiddenServiceStartObserver

class TorHiddenServiceStartObserver(HiddenServiceStartObserver):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
    def update(self):
        emit_service_start()
        repository = ContactRepository()
        approved_addresses = list(map(lambda x: x.address, repository.get_all_approved()))
        broker: Broker = InstanceContainer.resolve(Broker)
        for address in approved_addresses:
            auth_command = AuthenticationCommand()
            payload = Payload(auth_command, ConnectionSettings(address, TorConfiguration.get_tor_server_port()))
            self._logger.info(f'Sending Auth to {address}')
            broker.send(payload)


class OfflineEmitterAgentRemoveCallback(AgentRemoveCallback):
    def on_agent_removed(self, agent: Agent):
        repository = ContactRepository()
        if agent.address:
            contact = repository.get_by_address(agent.address)
            if contact and contact.approved and not contact.awaiting_approval:
                emit_contact_offline(contact)


class OfflineEmitterConnectionFailureCallback(ConnectionFailureCallback):
    def on_connection_failure(self, address: str):
        repository = ContactRepository()
        contact = repository.get_by_address(address)
        if contact and contact.approved and not contact.awaiting_approval:
            emit_contact_offline(contact)