import os
 
# Путь к PDF-документам
PDF_DOCS_DIR = os.path.join(os.getcwd(), "pdf_docs")
 
# Путь для сохранения векторного индекса (Chroma)
CHROMA_PERSIST_DIR = os.path.join(os.getcwd(), "chroma_index")
 
# Настройки для поддержки (подумаем как это прикрутить, если у модели плохой ответ)
SUPPORT_EMAIL = "pp-tender@mos.ru"
SUPPORT_PHONES = "8(800)303-12-34, 8(495)870-12-34"
ANSWER_FOR_SUPPORT_HELP = (f"Извините, я не смог найти информацию для ответа на ваш запрос. "
                        f"Рекомендуем обратиться в службу поддержки Портала Поставщиков: "
                        f"эл. почта {SUPPORT_EMAIL}, тел. {SUPPORT_PHONES}.")
 
# Модель для генерации эмбеддингов (SentenceTransformer)
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" #"intfloat/multilingual-e5-large"


# Модель для классификации (zero-shot) – модель для XNLI
CLASSIFIER_MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
 
# Локальная LLM для генерации ответов (YandexGPT-5 Lite Instruct)
LLM_MODEL_NAME = "yandex/YandexGPT-5-Lite-8B-instruct"
MAX_TRIES_TO_GET_CORRECT_TEXT_GENERATION = 2
 
# Параметры генерации ответа
MAX_NEW_TOKENS = 500
TEMPERATURE = 0.2

#Параметры для разделения текста PDF файлов на чанки
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200