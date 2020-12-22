from app.api.socket_emitter import emit_service_start
from app.networking.base import HiddenServiceStartObserver

class TorHiddenServiceStartObserver(HiddenServiceStartObserver):
    def update(self):
        emit_service_start()