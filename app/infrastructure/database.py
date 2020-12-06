from peewee import Model, SqliteDatabase

from app.shared.config import DatabaseConfiguration
from app.shared.helpful_abstractions import Singleton


class DatabaseContext(metaclass=Singleton):
    def __init__(self):
        self._database = SqliteDatabase(DatabaseConfiguration.get_database_path())


class BaseModel(Model):
    class Meta:
        database = DatabaseContext()