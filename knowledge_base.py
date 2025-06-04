__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import pandas as pd
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from config import PDF_DOCS_DIR, CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP
 
def load_documents_from_pdfs():
    """
    Загружает все PDF из папки pdf_docs и возвращает список документов.
    Каждый документ - объект langchain Document.
    """
    documents = []
    for filename in os.listdir(PDF_DOCS_DIR):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(PDF_DOCS_DIR, filename)
            loader = PyPDFLoader(file_path)
            docs = loader.load()  # список документов (по страницам)
            # Добавляем метаданные – имя файла
            for doc in docs:
                doc.metadata["source"] = filename
            documents.extend(docs)
    return documents

def load_documents_from_excel(file_path: str):
    """
    Загружает статьи из Excel-файла и возвращает список документов.
    Каждый документ – объект LangChain Document с указанием источника.
    """
    documents = []
    # Читаем Excel-файл (две колонки: тема и содержание)
    df = pd.read_excel(file_path)
    print("Размер таблицы",df.shape)
    for _, row in df.iterrows():
        # Извлекаем тему и содержание (приводим к строке на случай наличия чисел/NaN)
        topic = str(row["Заголовок статьи"]) if "Заголовок статьи" in df.columns else str(row[df.columns[0]])
        content = str(row["Описание"]) if "Описание" in df.columns else str(row[df.columns[1]])
        # Создаём документ с нужным форматом источника
        doc = Document(
            page_content=content,
            metadata={"source": f"статья с сайта портал поставщиков: {topic}"}
        )
        documents.append(doc)
    return documents
 
def split_documents(documents):
    """
    Разбивает документы на более мелкие фрагменты.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    docs_split = text_splitter.split_documents(documents)
    return docs_split
 
def build_vector_store():
    """
    Загружает или создает Chroma векторное хранилище.
    """
    if os.path.exists(CHROMA_PERSIST_DIR) and os.listdir(CHROMA_PERSIST_DIR):
        print("🔄 Загружаем существующий Chroma индекс...")
        return load_vector_store()

    print("🆕 Индекс не найден. Загружаем документы и создаём новый...")
    documents = []
    # Загрузка документов из PDF (постранично)
    documents.extend(load_documents_from_pdfs())
    # Загрузка документов из Excel, если файл существует
    excel_path = "./arcticles.xls"
    if os.path.exists(excel_path):
        documents.extend(load_documents_from_excel(excel_path))
    # Разбиение всех документов на фрагменты текста
    docs_split = split_documents(documents)
    # Инициализация эмбеддингов и векторного хранилища
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = Chroma.from_documents(
        docs_split, embedding=embeddings, persist_directory=CHROMA_PERSIST_DIR
    )
    vector_store.persist()
    print("✅ Индекс сохранён.")
    return vector_store


def load_vector_store():
    """
    Загружает ранее сохранённое векторное хранилище Chroma.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    return vector_store

if __name__ == "__main__":
    # Для предварительной индексации: запуск из командной строки
    vs = build_vector_store()
    print(f"Индекс построен, число фрагментов: {len(vs._collection.get()['documents'])}")