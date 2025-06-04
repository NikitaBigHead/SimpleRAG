from typing import List, Tuple

from .base_dao import BaseDAO
from .constants import CANDIDATE_LABELS


class LabelDAO(BaseDAO):
    """DAO для работы с темами"""
    def _init_db(self):
        self._execute('''
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')
        self._init_default_labels()

    def _init_default_labels(self):
        """Инициализация стандартных тем"""
        for label in CANDIDATE_LABELS:
            self._execute(
                "INSERT OR IGNORE INTO labels (name) VALUES (?)",
                (label,)
            )

    def get_all_labels(self) -> List[Tuple[int, str]]:
        cursor = self._execute('SELECT id, name FROM labels ORDER BY name')
        return cursor.fetchall()

    def get_label_name(self, label_id: int) -> str:
        cursor = self._execute('SELECT name FROM labels WHERE id = ?', (label_id,))
        return cursor.fetchone()[0]
