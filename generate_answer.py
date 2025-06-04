from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from config import LLM_MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE


@dataclass
class Document:
    """Класс для представления документа с контентом и метаданными."""
    page_content: str
    metadata: Dict[str, Any]


class AnswerGenerator:
    """
    Класс для генерации ответов на основе языковой модели и контекста из документов.
    
    Attributes:
        model_name (str): Название модели HuggingFace
        max_new_tokens (int): Максимальное количество новых токенов
        temperature (float): Температура генерации
        generator: Паплайн для генерации текста
    """
    
    def __init__(
        self,
        model_name: str = LLM_MODEL_NAME,
        max_new_tokens: int = MAX_NEW_TOKENS,
        temperature: float = TEMPERATURE,
        device_map: str = "auto",
        load_in_8bit: bool = True
    ):
        """
        Инициализирует генератор ответов.
        
        Args:
            model_name: Название модели
            max_new_tokens: Максимальное количество новых токенов
            temperature: Температура для креативности ответов
            device_map: Стратегия распределения по устройствам
            load_in_8bit: Использовать 8-битную квантизацию
        """
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.device_map = device_map
        self.load_in_8bit = load_in_8bit
        self.generator = self._init_generator()
    
    def _init_generator(self):
        """Инициализирует паплайн для генерации текста."""
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map=self.device_map,
            load_in_8bit=self.load_in_8bit
        )
        return pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature
        )
    
    def format_context(self, docs: List[Document]) -> str:
        """
        Форматирует контекст из документов для включения в промпт.
        
        Args:
            docs: Список документов
            
        Returns:
            str: Отформатированный контекст
        """
        context_parts = []
        for i, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", f"Документ_{i}")
            excerpt = doc.page_content[:300].replace("\n", " ")
            context_parts.append(f"Документ {i} ({source}): {excerpt}...")
        return "\n\n".join(context_parts)
    
    def generate_prompt(self, user_query: str, context: str) -> str:
        """
        Генерирует промпт для языковой модели.
        
        Args:
            user_query: Запрос пользователя
            context: Контекст из документов
            
        Returns:
            str: Полный промпт для модели
        """
        return (
            "Ты — интеллектуальный помощник для пользователей портала поставщиков. "
            "Используя информацию из нижеприведённых документов, дай подробный и точный ответ на вопрос. "
            # "Если информации недостаточно, сообщи об этом и предложи обратиться в службу поддержки, указав контакты.
            
            "Документы:\n"
            f"{context}\n\n"
            f"Вопрос: {user_query}\n\n"
            "Ответ:"
        )
    
    def generate_official_prompt(self, user_query: str) -> str:
        """
        Генерирует промпт для языковой модели.
        
        Args:
            user_query: Запрос пользователя
            context: Контекст из документов
            
        Returns:
            str: Полный промпт для модели
        """
        return (
            "Ты — интеллектуальный помощник для пользователей портала поставщиков. "
            "Вопрос пользователя пожалуйста перефразируй в официальном стиле.\n\n "
            f"Вопрос: {user_query}\n\n"
            "Ответ:"
        )
    

    def generate_prompt_diff_user_query_bot_answer(self, user_query: str, answer: str) -> str:
        """
        Генерирует промпт для языковой модели.
        
        Args:
            user_query: Запрос пользователя
            context: Контекст из документов
            
        Returns:
            str: Полный промпт для модели
        """
        return (
            "Ты — интеллектуальный помощник для пользователей портала поставщиков. "
            "Сейчас ты отвечаешь релевантный ли  ответ ты дал пользователю."
            "Напиши пожалуйста либо да, если ответ релевантный. Иначе напиши - нет.\n\n" 

            "Вопрос пользователя:\n"
            f"{user_query}\n\n"
            "Ответ модели:"
            f"{answer}\n\n"
            "Ответ:"
        )
    
    
    def generate_better_promt(self, user_query: str , answer: str) -> str: #answer: str
        """
        Генерирует промпт для языковой модели.
        
        Args:
            user_query: Запрос пользователя
            context: Контекст из документов
            
        Returns:
            str: Полный промпт для модели
        """
        return (
            "Ты — интеллектуальный помощник для пользователей портала поставщиков. "
            "Тебе на вход подается предидущие запросы пользователя. " #и ответы модели.
            "Перефразируй пожалуйста запрос пользователя так, чтобы он улучшил релевантность поиска информации по базе знаний.\n\n" 

            "Вопросы пользователя:\n"
            f"{user_query}\n\n"
            "ответы модели:"
            f"{answer}\n\n"
            "Ответ:"
        )
    

    

    def postprocess_answer(self, generated_text: str, prompt: str) -> str:
        """
        Постобработка сгенерированного ответа.
        
        Args:
            generated_text: Полный сгенерированный текст
            prompt: Промпт, который был передан модели
            
        Returns:
            str: Очищенный ответ
        """
        return generated_text[len(prompt):].strip()
    
    def extract_sources(self, docs: List[Document]) -> str:
        """
        Извлекает источники из списка документов, формируя строку с указанием 
        имени документа и при необходимости страницы или раздела.
        """
        if not docs:
            return "Неизвестный источник"
        sources_info = {}  # словарь: имя источника -> набор страниц/разделов
        for doc in docs:
            source_name = doc.metadata.get("source", "Неизвестный источник")
            page_num = doc.metadata.get("page")
            section_name = doc.metadata.get("section")
            # Инициализируем запись в словаре, если еще нет
            if source_name not in sources_info:
                sources_info[source_name] = {"pages": set(), "sections": set()}
            # Сохраняем номер страницы (если есть) и название раздела (если есть)
            if isinstance(page_num, int) or str(page_num).isdigit():
                sources_info[source_name]["pages"].add(int(page_num))
            if section_name:
                sources_info[source_name]["sections"].add(str(section_name))
        # Формируем строки для каждого источника
        source_strings = []
        for source, info in sources_info.items():
            if info["pages"]:
                # Если есть номера страниц, указываем их
                pages_list = sorted(info["pages"])
                if len(pages_list) == 1:
                    source_strings.append(f"{source} (стр. {pages_list[0]})")
                else:
                    # Если несколько страниц, перечисляем через запятую
                    pages_str = ", ".join(str(p) for p in pages_list)
                    source_strings.append(f"{source} (стр. {pages_str})")
            elif info["sections"]:
                # Если страниц нет, но есть названия разделов
                sections_str = ", ".join(info["sections"])
                source_strings.append(f"{source} (раздел: {sections_str})")
            else:
                # Ни страницы, ни раздела – выводим только источник
                source_strings.append(source)
        return "; ".join(source_strings)
    
    def get_answer(self, promt):
        generated = self.generator(promt)[0]["generated_text"]
        answer = self.postprocess_answer(generated, promt)
        return answer
        

    def generate_answer(self, user_query: str, docs: List[Document]) -> Tuple[str, str]:
        """
        Генерирует ответ на основе запроса пользователя и документов.
        
        Args:
            user_query: Запрос пользователя
            docs: Список релевантных документов
            
        Returns:
            Tuple[str, str]: Ответ и строка источников
        """

        context = self.format_context(docs)
        promt = self.generate_prompt(user_query, context)
        model_answer = self.get_answer(promt)
        sources = self.extract_sources(docs)

        return model_answer, sources

    
    def generate_official_query(self,user_query):
        promt = self.generate_official_prompt(user_query)
        model_answer = self.get_answer(promt)
        return model_answer
    
    def is_good_answer(self,user_query, model_answer):
        promt = self.generate_prompt_diff_user_query_bot_answer(user_query, model_answer)
        is_correct_model_answer = self.get_answer(promt)
        is_correct_answer = True if is_correct_model_answer == "да" else False
        return is_correct_answer
    
    def generate_new_query(self, user_queries, model_answers):
        user_queries = "\n".join(user_queries)
        model_answers = "\n".join(model_answers)
        promt = self.generate_better_promt(user_queries, model_answers) #
        new_query = self.get_answer(promt)

        return new_query

if __name__ == "__main__":
    # Пример использования
    generator = AnswerGenerator()
    
    # Тестовые документы
    docs = [
        Document(
            page_content="Для регистрации необходимо нажать на кнопку 'Регистрация' и заполнить форму.",
            metadata={"source": "Инструкция_по_работе_с_Порталом.pdf"}
        ),
        Document(
            page_content="После регистрации требуется подтверждение email и проверка данных модератором.",
            metadata={"source": "Правила_портала.docx"}
        )
    ]
    
    #query = "Как зарегистрироваться на портале поставщиков?"
    query = "Как осуществляется электронное исполнение контракта, и чем оно отличается от бумажного исполнения?"

    answer, sources = generator.generate_answer(query, docs)
    
    print("Вопрос:", query)
    print("Ответ:", answer)
    print("Источники:", sources)