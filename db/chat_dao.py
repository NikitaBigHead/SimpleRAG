from  datetime import datetime
from typing import List, Tuple
from .base_dao import BaseDAO
from .constants import DATE_FORMAT

class ChatDAO(BaseDAO):
    """DAO для работы с чатами"""
    def _init_db(self):
        self._execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT DEFAULT 'Новый чат',
                created_at DATETIME,
                deleted BOOL DEFAULT FALSE
            )
        ''')

    def create_chat(self, title: str = "Новый чат") -> int:
        cursor = self._execute(
            'INSERT INTO chats (title, created_at) VALUES (?, ?)',
            (title, datetime.now().strftime(DATE_FORMAT)))
        return cursor.lastrowid

    def get_all_chats(self) -> List[Tuple[int, str, str]]:
        cursor = self._execute(
            'SELECT id, title, created_at FROM chats WHERE deleted = false  ORDER BY created_at DESC')
        return cursor.fetchall()

    def delete_chat(self, chat_id: int):
        self._execute(
            'UPDATE chats SET deleted = ? WHERE id = ?',
            (True, chat_id))

    def update_chat_title(self, chat_id: int, new_title: str):
        self._execute(
            'UPDATE chats SET title = ? WHERE id = ?',
            (new_title, chat_id))