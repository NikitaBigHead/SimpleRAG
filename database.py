import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

DB_PATH = "history.db"

class InteractionLogger:
    """
    Класс для логирования взаимодействий с пользователем в SQLite базе данных.
    
    Attributes:
        db_path (str): Путь к файлу базы данных
        conn (sqlite3.Connection): Соединение с базой данных
        cursor (sqlite3.Cursor): Курсор для выполнения запросов
    """
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Инициализирует соединение с базой данных и создает таблицу при необходимости.
        
        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()
    
    def _init_db(self) -> None:
        """Создает таблицу history, если она не существует."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_query TEXT,
                category TEXT,
                answer TEXT,
                sources TEXT,
                rating INTEGER,
                frequency INTEGER
            )
        """)
        self.conn.commit()
    
    def log_interaction(
        self,
        user_query: str,
        category: str,
        answer: str,
        sources: str
    ) -> int:
        """
        Логирует взаимодействие с пользователем.
        
        Args:
            user_query: Текст запроса пользователя
            category: Категория запроса
            answer: Текст ответа
            sources: Источники, использованные для формирования ответа
            
        Returns:
            int: ID созданной или обновленной записи
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Проверяем существование такого же запроса
        self.cursor.execute(
            "SELECT id, frequency FROM history WHERE user_query = ?", 
            (user_query,)
        )
        row = self.cursor.fetchone()
        
        if row:
            # Обновляем существующую запись
            record_id, freq = row
            self.cursor.execute("""
                UPDATE history 
                SET frequency = ?, timestamp = ?, category = ?, answer = ?, sources = ?, rating = NULL 
                WHERE id = ?
            """, (freq + 1, timestamp, category, answer, sources, record_id))
        else:
            # Создаем новую запись
            self.cursor.execute("""
                INSERT INTO history (
                    timestamp, user_query, category, answer, sources, rating, frequency
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, user_query, category, answer, sources, None, 1))
            record_id = self.cursor.lastrowid
        
        self.conn.commit()
        return record_id
    
    def update_rating(self, record_id: int, rating_value: int) -> None:
        """
        Обновляет оценку для указанной записи.
        
        Args:
            record_id: ID записи в базе данных
            rating_value: Значение оценки (целое число)
        """
        self.cursor.execute(
            "UPDATE history SET rating = ? WHERE id = ?", 
            (rating_value, record_id)
        )
        self.conn.commit()
    
    def get_history(self, limit: int = 10) -> List[Tuple]:
        """
        Возвращает историю взаимодействий.
        
        Args:
            limit: Максимальное количество возвращаемых записей
            
        Returns:
            List[Tuple]: Список записей из истории
        """
        self.cursor.execute(
            "SELECT timestamp, user_query, category, rating FROM history ORDER BY id DESC LIMIT ?", 
            (limit,)
        )
        return self.cursor.fetchall()
    
    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        self.conn.close()
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера."""
        self.close()


if __name__ == "__main__":
    # Пример использования
    with InteractionLogger() as logger:
        # Логируем новое взаимодействие
        record_id = logger.log_interaction(
            user_query="Как сбросить пароль?",
            category="техническая поддержка",
            answer="Для сброса пароля перейдите на страницу восстановления...",
            sources="База знаний, статья 123"
        )
        print(f"Запись добавлена с ID: {record_id}")
        
        # Обновляем оценку
        logger.update_rating(record_id, 5)
        
        # Получаем историю
        history = logger.get_history()
        print("\nПоследние записи:")
        for record in history:
            print