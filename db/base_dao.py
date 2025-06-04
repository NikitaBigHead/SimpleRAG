import sqlite3

from .constants import DATABASE_NAME

class BaseDAO:
    """Базовый класс для работы с базой данных"""
    def __init__(self, db_name: str = DATABASE_NAME):
        self.db_name = db_name
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        with self._connect() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor

    def _init_db(self):
        """Инициализация структуры базы данных"""
        raise NotImplementedError("Должен быть реализован в дочерних классах")
