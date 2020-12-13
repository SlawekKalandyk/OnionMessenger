from peewee import Model, SqliteDatabase

from app.shared.config import DatabaseConfiguration
from app.shared.helpful_abstractions import Singleton

class DatabaseContext():
    def __init__(self):
        self._database = SqliteDatabase(DatabaseConfiguration.get_database_path(), pragmas={\
            'journal_mode': 'wal',\
            'cache_size': 10000,\
            'foreign_keys': 1,\
            'synchronous': 0\
        })

    def transaction(self):
        return self._database.atomic()

    def create_tables_if_not_exist(self, tables):
        self._database.create_tables(tables)

    def connect_to_database(self):
        self._database.connect()
        return self

    def close(self):
        self._database.close()

class BaseModel(Model):
    class Meta:
        database = DatabaseContext()._database