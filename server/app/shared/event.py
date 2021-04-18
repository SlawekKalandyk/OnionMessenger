class Event:
    def __init__(self):
        self.listeners = []

    def __iadd__(self, listener):
        """Shortcut for using += to add a listener."""
        self.listeners.append(listener)
        return self

    def __isub__(self, listener):
        """Shortcut for using -= to remvoe a listener."""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def notify(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)