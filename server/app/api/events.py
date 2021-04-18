from app.networking.topology import Agent
from app.shared.config import TorConfiguration
from app.messaging.broker import Broker, Payload
from app.shared.container import InstanceContainer
from app.infrastructure.contact import ContactRepository
from app.api.socket_emitter import emit_contact_offline, emit_service_start
from app.api.commands import AuthenticationCommand
from app.networking.base import ConnectionSettings


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