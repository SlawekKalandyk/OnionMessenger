from typing import Any, Dict, List, Tuple


class InstanceContainer:
    _transients: Dict[type, type] = dict()
    _singletons: Dict[type, object] = dict()

    @staticmethod
    def register_singleton(register_type, instance):
        if InstanceContainer._transients[register_type]:
            InstanceContainer._transients[register_type] = None
        InstanceContainer._singletons[register_type] = instance

    @staticmethod
    def register_transient(register_type):
        if InstanceContainer._singletons[register_type]:
            InstanceContainer._singletons[register_type] = None
        InstanceContainer._transients[register_type] = register_type

    @staticmethod
    def resolve(registered_type):
        if InstanceContainer._transients[registered_type]:
            return InstanceContainer._transients[registered_type]()
        elif InstanceContainer._singletons[registered_type]:
            return InstanceContainer._singletons[registered_type]
        else:
            raise TypeNotInContainerError()
        

class TypeNotInContainerError(Exception):
    pass