from __future__ import annotations
from dataclasses import dataclass, InitVar, field
from dataclasses_json import dataclass_json
from abc import ABC, abstractmethod
from typing import Any, List


class Receiver(ABC):
    pass


@dataclass_json
@dataclass(frozen=True)
class Command(ABC):
    source: str
    
    @classmethod
    @abstractmethod
    def get_identifier(cls) -> str:
        pass

    @abstractmethod
    def invoke(self, receiver: Receiver) -> List[Command]:
        pass