from time import time
from app.shared.config import TorConfiguration
from app.networking.base import ConnectionSettings
from app.messaging.broker import Broker, Payload
from app.infrastructure.saved_command import SavedCommandRepository
from app.networking.topology import Agent
from app.shared.config import TorConfiguration
from app.shared.container import InstanceContainer
from app.infrastructure.contact import ContactRepository
from app.api.socket_emitter import emit_contact_offline, emit_service_start
from app.api.commands import AuthenticationCommand

class BacklogHandler:
    def __init__(self):
        self._backlog_send_interval = 90
        self._last_backlog_check_time = time() - self._backlog_send_interval

    def handle_backlog(self, broker: Broker):
        current = time()
        diff = current- self._last_backlog_check_time
        if diff > self._backlog_send_interval:
            self._last_backlog_check_time = current
            saved_command_repository = SavedCommandRepository()
            initiating_commands = saved_command_repository.get_all_initiating()
            for saved_command in initiating_commands:
                connection_settings = ConnectionSettings(saved_command.interlocutor.address, TorConfiguration.get_tor_server_port())
                payload = Payload(saved_command.command, connection_settings)
                broker.send(payload)


def on_hidden_service_start():
    emit_service_start()
    repository = ContactRepository()
    approved_addresses = list(map(lambda x: x.address, repository.get_all_approved()))
    broker: Broker = InstanceContainer.resolve(Broker)
    broker.service_started = True
    for address in approved_addresses:
        auth_command = AuthenticationCommand()
        payload = Payload(auth_command, ConnectionSettings(address, TorConfiguration.get_tor_server_port()))
        broker.send(payload)


def on_agent_removed(agent: Agent):
    repository = ContactRepository()
    if agent.address:
        contact = repository.get_by_address(agent.address)
        if contact and contact.approved and not contact.awaiting_approval:
            emit_contact_offline(contact)


def on_connection_failure(address: str):
    repository = ContactRepository()
    contact = repository.get_by_address(address)
    if contact and contact.approved and not contact.awaiting_approval:
        emit_contact_offline(contact)