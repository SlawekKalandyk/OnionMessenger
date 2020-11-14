from abc import ABC, abstractmethod

class Closable(ABC):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @abstractmethod
    def close(self):
        pass