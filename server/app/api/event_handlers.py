from time import time
from app.shared.config import TorConfiguration
from app.networking.base import ConnectionSettings
from app.messaging.broker import Broker, Payload
from app.infrastructure.saved_command import SavedCommandRepository

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
