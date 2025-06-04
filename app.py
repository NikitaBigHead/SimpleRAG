import random
from datetime import datetime
import streamlit as st
from typing import Optional

from preprocess import preprocess_query
from classification import ZeroShotQueryClassifier
from generate_answer import AnswerGenerator
from database import InteractionLogger
from knowledge_base import build_vector_store
from langchain.vectorstores import Chroma
from config import ANSWER_FOR_SUPPORT_HELP, MAX_TRIES_TO_GET_CORRECT_TEXT_GENERATION

from db import CANDIDATE_LABELS, DATE_FORMAT, ChatDAO, MessageDAO, LabelDAO
from page_template import create_template

from PIL import Image

st.set_page_config(page_title="Помощник Портала Поставщиков",
                   layout="wide",
                   page_icon=Image.open("static/logo.png"))

create_template()


# Инициализация
@st.cache_resource
def init_classifier() -> ZeroShotQueryClassifier:
    return ZeroShotQueryClassifier()


@st.cache_resource
def init_answerGenerator() -> AnswerGenerator:
    return AnswerGenerator()


@st.cache_resource
def init_db() -> InteractionLogger:
    return InteractionLogger()


@st.cache_resource
def init_vector_store() -> Chroma:
    return build_vector_store()


classifier = init_classifier()
answerGenerator = init_answerGenerator()
interactionLogger = init_db()
vector_store = init_vector_store()

# Загрузка/построение векторного индекса (это выполняется при старте)
with st.spinner("Индексация документов..."):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})


class ChatInterface:
    """Класс для управления пользовательским интерфейсом чата"""

   
    def __init__(self):
        self.chat_dao = ChatDAO()
        self.message_dao = MessageDAO()
        self.label_dao = LabelDAO()

    def render_sidebar(self):
        """Отрисовка боковой панели с чатами"""
        with st.sidebar:
            self._render_new_chat_button()
            self._render_chat_history()

    def _render_new_chat_button(self):
        """Кнопка создания нового чата"""
        if st.button("Новый чат", use_container_width=True):
            new_chat_id = self.chat_dao.create_chat()
            st.session_state.current_chat = new_chat_id
            st.rerun()

    def _render_chat_history(self):
        """Отображение истории чатов"""
        st.subheader("История чатов")
        chats = self.chat_dao.get_all_chats()

        for chat in chats:
            self._render_chat_button(chat)

    def _render_chat_button(self, chat: tuple):
        """Отрисовка кнопки чата в истории"""
        chat_id, title, created_at = chat
        formatted_date = datetime.strptime(
            created_at, DATE_FORMAT).strftime('%d.%m %H:%M')

        # Форматирование отображаемого названия
        display_title = (title[:15] + '...') if len(title) > 18 else title
        button_label = f"{display_title} ({formatted_date})"

        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                    button_label,
                    key=f"chat_{chat_id}",
                    use_container_width=True
            ):
                st.session_state.current_chat = chat_id
                st.rerun()

        with col2:
            with st.popover("⚙️"):
                self._render_chat_management_menu(chat_id, title)

    def _render_chat_management_menu(self, chat_id: int, current_title: str):
        """Меню управления чатом"""
        new_title = st.text_input(
            "Новое название",
            value=current_title,
            key=f"rename_{chat_id}"
        )

        if st.button("✏️ Переименовать", key=f"rename_btn_{chat_id}", use_container_width=True):
            if new_title.strip():
                self.chat_dao.update_chat_title(chat_id, new_title.strip())
                st.rerun()
            else:
                st.error("Название не может быть пустым")

        if st.button("🗑️ Удалить", key=f"delete_{chat_id}", use_container_width=True):
            if st.session_state.current_chat == chat_id:
                st.session_state.current_chat = None
            self._delete_chat(chat_id)
            st.rerun()

    def _delete_chat(self, chat_id: int):
        """Удаление чата"""
        self.chat_dao.delete_chat(chat_id)
        self.message_dao.delete_messages(chat_id)

    def render_main_interface(self):
        """Отрисовка основного интерфейса чата"""
        if not st.session_state.current_chat:
            self._render_empty_state()
            return

        self._render_chat_header()
        messages = self.message_dao.get_messages(st.session_state.current_chat)
        self._render_messages(messages)
        self._handle_user_query()

    def _render_empty_state(self):
        """Отображение состояния при отсутствии выбранного чата"""
        st.info("Создайте новый чат или выберите существующий из списка слева")

    def _render_chat_header(self):
        """Заголовок чата с возможностью редактирования"""
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.header(self._get_current_chat_title())

    def _get_current_chat_title(self) -> str:
        """Получение текущего названия чата"""
        chats = self.chat_dao.get_all_chats()
        for chat in chats:
            if chat[0] == st.session_state.current_chat:
                return chat[1]
        return "Неизвестный чат"

    def _render_messages(self, messages: list):
        """Отображение всех сообщений чата"""
        for i, msg in enumerate(messages):
            if i == len(messages) - 1:
                self._render_message(msg)
                continue
            self._render_message(msg)

    def _render_message(self, msg: tuple):
        """Отрисовка отдельного сообщения"""
        message_id, role, content, sources, timestamp, rating, label_id = msg
        with st.chat_message(role):
            st.write(content)
            if sources:
                st.write(sources)

            if role == 'assistant':
                self._render_rating_control(message_id, rating)
            else:

                if isinstance(label_id, int):
                    st.write(f"**Категория:** {CANDIDATE_LABELS[label_id]}")

            st.caption(timestamp)

    def _render_rating_control(self, message_id: int,
                               current_rating: Optional[int] = None, ):
        """Контрол оценки для сообщений ассистента"""

        rating = st.radio("Ваша оценка:", options=["👎 Не помогает", "👍 Полезно"],
                          key=f"rating_{message_id}", horizontal=True,
                          index=None if current_rating is None else current_rating)

        if st.button("Сохранить оценку", key=f"save_raiting_{message_id}"):
            rating_value = 1 if rating == "👍 Полезно" else 0
            self.message_dao.update_field(message_id, 'rating', rating_value)
            st.success("Спасибо! Ваша оценка сохранена.")

    def _handle_user_query(self):
        """Обработка пользовательского ввода"""
        if user_query := st.chat_input("Введите сообщение..."):
            self._process_user_query(user_query)

    def _process_user_query(self, user_query: str):
        """Обработка нового сообщения пользователя"""
        # Автогенерация названия чата при первом сообщении
        if self._is_first_message_in_chat():
            self._generate_chat_title(user_query)

        # Сохранение сообщения пользователя
        msg_id = self.message_dao.add_message(
            st.session_state.current_chat,
            'user',
            user_query
        )
        self._render_message(self.message_dao.get_message(msg_id))
        with st.spinner("Wait for it...", show_time=True):
            # Генерация и сохранение ответа бота
            self._generate_bot_response(user_query)
            st.rerun()

    def _is_first_message_in_chat(self) -> bool:
        """Проверка, является ли сообщение первым в чате"""
        messages = self.message_dao.get_messages(st.session_state.current_chat)
        return len(messages) == 0

    def _generate_chat_title(self, first_message: str):
        """Генерация названия чата на основе первого сообщения"""
        auto_title = (first_message[:30] + "...") if len(first_message) > 30 else first_message
        self.chat_dao.update_chat_title(
            st.session_state.current_chat,
            auto_title
        )

    def _generate_bot_response(self, user_query: str):
        """Генерация ответа бота (заглушка)"""

        buffer_queries = []
        buffer_answers = []
        is_correct_answer = False
        
        user_query = user_query.strip("\n ")

        for i in range(MAX_TRIES_TO_GET_CORRECT_TEXT_GENERATION):
            
            user_query = answerGenerator.generate_official_query(user_query)
            # Предобработка запроса
            processed_query = preprocess_query(user_query)
            # Классификация запроса
            category = classifier.classify(user_query)
    
            # Поиск релевантных документов
            relevant_docs = retriever.get_relevant_documents(processed_query)

            try:
                answer, sources = answerGenerator.generate_answer(user_query, relevant_docs)
            except RuntimeError:
                is_correct_answer = False
                continue

            is_correct_answer = answerGenerator.is_good_answer(user_query, answer)

            if is_correct_answer:
                break

            buffer_queries.append(user_query)
            buffer_answers.append(answer)

            user_query = answerGenerator.generate_new_query(buffer_queries, buffer_answers)


        last_label_id = CANDIDATE_LABELS.index(category)
        self.message_dao.update_field(self.message_dao.get_messages(st.session_state.current_chat)[-1][0],
                                        "label_id", last_label_id)
            
        answer = f"**Ответ:** {answer}"
        sources = f"**Использованные источники:** {sources}"

        # запись в БД
        self.message_dao.add_message(
            st.session_state.current_chat,
            'assistant',
            answer,
            last_label_id,
            sources,
        )


def main():
    chat_interface = ChatInterface()
    chat_interface.render_sidebar()
    chat_interface.render_main_interface()


if __name__ == "__main__":
    main()
