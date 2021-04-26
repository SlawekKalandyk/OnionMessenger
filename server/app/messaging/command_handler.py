from __future__ import annotations
import logging
from typing import Any, Dict, Iterable, Optional
from abc import ABC, abstractmethod

from app.messaging.base import Command

class BaseCommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command) -> Iterable[Command]:
        pass


class CommandHandler(BaseCommandHandler):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def handle(self, command: Command) -> Iterable[Command]:
        self._logger.info(f'Handling {command}')
        responses: Iterable[Command] = command.invoke()
        if responses:
            for response in responses:
                yield response
