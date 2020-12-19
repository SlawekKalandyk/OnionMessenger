from typing import Dict


class InstanceContainer:
    _transients: Dict[type, type] = dict()
    _singletons: Dict[type, object] = dict()

    @staticmethod
    def register_singleton(register_type, instance):
        if register_type in InstanceContainer._transients:
            InstanceContainer._transients[register_type] = None
        InstanceContainer._singletons[register_type] = instance

    @staticmethod
    def register_transient(register_type):
        if register_type in InstanceContainer._singletons:
            InstanceContainer._singletons[register_type] = None
        InstanceContainer._transients[register_type] = register_type

    @staticmethod
    def resolve(registered_type):
        if registered_type in InstanceContainer._transients:
            return InstanceContainer._transients[registered_type]()
        elif registered_type in InstanceContainer._singletons:
            return InstanceContainer._singletons[registered_type]
        else:
            raise TypeNotInContainerError()
        

class TypeNotInContainerError(Exception):
    pass