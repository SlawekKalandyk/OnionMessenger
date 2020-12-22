from __future__ import annotations
from typing import Any, Dict, Iterable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from app.messaging.base import Command, CommandMapper

class BaseCommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command) -> Iterable[Command]:
        pass


class CommandHandler(BaseCommandHandler):
    def __init__(self, command_mapper: CommandMapper):
        self._registered_types: Dict[type, Any] = dict()
        self._command_mapper = command_mapper

    def register(self, command_type: type, receiver: Any) -> CommandHandler:
        if receiver is None:
            raise NoneReceiverException(command_type)
        self._registered_types[command_type] = receiver
        return self

    def handle(self, command: Command) -> Iterable[Command]:
        receiver = self._get_receiver(command)
        responses: Iterable[Command] = command.invoke(receiver)
        if responses:
            for response in responses:
                yield response

    # pylint: disable=unsubscriptable-object
    def _get_receiver(self, command: Command) -> Optional[Any]:
        for registered_type, receiver in self._registered_types.items():
            if isinstance(command, registered_type):
                return receiver
        raise CommandNotRegisteredException(command)


class NoneReceiverException(Exception):
    pass


class CommandNotRegisteredException(Exception):
    pass