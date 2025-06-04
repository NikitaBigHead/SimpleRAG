from datetime import datetime
from typing import List, Tuple, Optional

from pyasn1_modules.rfc2985 import messageDigest

from .base_dao import BaseDAO
from .constants import DATE_FORMAT


class MessageDAO(BaseDAO):
    """DAO для работы с сообщениями"""

    def _init_db(self):
        self._execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                sources TEXT DEFAULT NULL,
                timestamp DATETIME,
                rating INTEGER DEFAULT NULL,
                label_id INTEGER DEFAULT NULL,
                deleted BOOL DEFAULT FALSE,
                FOREIGN KEY(chat_id) REFERENCES chats(id),
                FOREIGN KEY(label_id) REFERENCES labels(id)
            )
        ''')

    def get_message(self, message_id: int) -> Tuple:
        cursor = self._execute('''
            SELECT m.id, m.role, m.content, m.sources, m.timestamp, m.rating, m.label_id 
            FROM messages m
            WHERE id = ? 
            ORDER BY timestamp ASC''',
                               (message_id,))
        return cursor.fetchone()

    def get_messages(self, chat_id: int) -> List[Tuple]:
        cursor = self._execute('''
            SELECT m.id, m.role, m.content, m.sources, m.timestamp, m.rating, m.label_id 
            FROM messages m
            WHERE chat_id = ? 
            ORDER BY timestamp ASC''',
                               (chat_id,))
        return cursor.fetchall()

    def add_message(self, chat_id: int,
                    role: str,
                    content: str,
                    label_id: Optional[int] = None,
                    sources: Optional[str] = None) -> int:
        cursor = self._execute(
            '''INSERT INTO messages 
               (chat_id, role, content, sources, rating, label_id, timestamp)
               VALUES (?, ?, ?, ?, NULL, ?, ?)''',
            (chat_id, role, content, sources, label_id, datetime.now().strftime(DATE_FORMAT)))
        return cursor.lastrowid

    def update_field(self, message_id: int, field: str, value: str | int) -> None:
        allowed_fields = {'rating', 'label_id'}
        if field not in allowed_fields:
            raise ValueError(f"Недопустимое поле для обновления: {field}")
        self._execute(
            f'UPDATE messages SET {field} = ? WHERE id = ?',
            (value, message_id))

    def delete_messages(self, chat_id: int):
        self._execute(
            'UPDATE messages SET deleted = ? WHERE chat_id = ?',
            (True, chat_id))

    def get_number_of_messages(self, label_id, rating):
        if rating is None:
            cursor = self._execute(''' 
                SELECT COUNT(*) 
                FROM messages 
                WHERE label_id = ? AND rating IS NULL AND deleted = FALSE AND role = 'assistant'
                ''', (label_id,))
        else:
            cursor = self._execute(''' 
                SELECT COUNT(*) 
                FROM messages 
                WHERE label_id = ? AND rating = ? AND deleted = FALSE AND role = 'assistant'
                ''', (label_id, rating))

        return cursor.fetchone()[0]
