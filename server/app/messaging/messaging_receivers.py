from app.networking.topology import Topology
from app.messaging.base import Receiver
from dataclasses import dataclass


@dataclass
class ImAliveCommandReceiver(Receiver):
    topology: Topology