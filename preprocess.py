# Здесь реализована работа с текстом, которая указана в тз:\
#  например поиск синонимов, обработка опечаток и т.п

import re
from difflib import get_close_matches
 
# Пример списка часто встречающихся терминов из базы знаний (расширите по необходимости)
GLOSSARY_TERMS = [
    "регистрация", "портал", "закупка", "контракт", "поддержка", "техподдержка",
    "инструкция", "информационное", "система", "поставщик", "заказчик", "оферта"
]
 
# Пример словаря синонимов
SYNONYMS = {
    "закупка": ["тендер", "покупка"],
    "контракт": ["договор"],
    "поддержка": ["техподдержка", "саппорт"]
}
 
def preprocess_query(query: str, glossary_terms=GLOSSARY_TERMS) -> str:
    """
    Выполняет нормализацию текста: приведение к нижнему регистру, удаление лишних символов,
    исправление опечаток по известным терминам и расширение синонимами.
    """
    q = query.lower().strip()
    q = re.sub(r"[^\w\s\u0400-\u04FF]", " ", q)  # оставляем буквы (включая кириллицу) и цифры
    words = q.split()
    corrected_words = []
    for word in words:
        # Ищем близкое соответствие из glossary_terms с cutoff=0.8
        matches = get_close_matches(word, glossary_terms, cutoff=0.8)
        corrected_words.append(matches[0] if matches else word)
    q = " ".join(corrected_words)
    # Добавляем синонимы, если слово найдено в словаре
    expanded = []
    for word in q.split():
        expanded.append(word)
        if word in SYNONYMS:
            expanded.extend(SYNONYMS[word])
    return " ".join(expanded)
 
if __name__ == "__main__":
    sample = "Как зарегестрироваться на портале?"
    print(preprocess_query(sample))