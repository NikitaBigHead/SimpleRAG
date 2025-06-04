from transformers import pipeline
from config import CLASSIFIER_MODEL_NAME
from typing import List
from db import CANDIDATE_LABELS

class ZeroShotQueryClassifier:
    """
    Класс для классификации текстовых запросов с использованием zero-shot классификации.
    
    Attributes:
        classifier (pipeline): Паплайн для zero-shot классификации
        candidate_labels (List[str]): Список возможных категорий для классификации
    """
    
    def __init__(self, model_name: str = CLASSIFIER_MODEL_NAME, 
                 candidate_labels: List[str] = CANDIDATE_LABELS):
        """
        Инициализирует классификатор.
        
        Args:
            model_name: Название модели для классификации
            candidate_labels: Список возможных категорий. Если None, будет использован стандартный набор.
        """
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.candidate_labels = candidate_labels
    
    def classify(self, query: str) -> str:
        """
        Классифицирует текстовый запрос.
        
        Args:
            query: Текст запроса для классификации
            
        Returns:
            str: Название наиболее подходящей категории
        """
        result = self.classifier(
            query, 
            candidate_labels=self.candidate_labels, 
            hypothesis_template="Это {}."
        )
        return result["labels"][0]


if __name__ == "__main__":
    # Пример использования
    classifier = ZeroShotQueryClassifier()
    sample_query = "Я не могу зайти в личный кабинет, появляется ошибка"
    print("Категория:", classifier.classify(sample_query))