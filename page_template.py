import streamlit as st
from PIL import Image

import base64


def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def create_template():
    """Создание шаблона страницы"""
    hide_streamlit_elements = """
        <style>
        #MainMenu {visibility: hidden;}            /* Убираем три палочки */
        footer {visibility: hidden;}               /* Убираем футер */
        [data-testid="stToolbar"] { display: none; } /* Убираем кнопку Deploy */
        .css-1v0mbdj.edgvbvh3 {display: none;}     /* Убираем "Running..." */
        </style>
    """
    st.markdown(hide_streamlit_elements, unsafe_allow_html=True)

    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None

    icon = Image.open("static/logo.png")  # Укажите путь к вашей иконке
    st.logo(icon)
    icon_base64 = get_image_base64("static/logo.png")

    # HTML-шаблон с иконкой и заголовком
    html = f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="data:image/png;base64,{icon_base64}" style="height: 90px;"/>
        <h1 style='margin: 0;'>Помощник Портала Поставщиков</h1>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    hide_default_sidebar = '''
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
    '''
    st.markdown(hide_default_sidebar, unsafe_allow_html=True)

    with st.sidebar:
        st.page_link("app.py", label="Чаты", icon="🏠")
        st.page_link("pages/analysis.py", label="Аналитика", icon="📈")
    st.write(" ")