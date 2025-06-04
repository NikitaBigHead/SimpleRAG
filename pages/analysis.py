import streamlit as st
import pandas as pd
from db import CANDIDATE_LABELS, MessageDAO
from page_template import create_template
from PIL import Image

st.set_page_config(page_title="Помощник Портала Поставщиков",
                   layout="wide",
                   page_icon = Image.open("static/logo.png"))

# st.title("🤖 Помощник Портала Поставщиков")

create_template()


message_dao = MessageDAO()

data = [[] for i in range(4)]

for i in range(4):
    data[i].append(message_dao.get_number_of_messages(i, None))
    data[i].append(message_dao.get_number_of_messages(i, 0))
    data[i].append(message_dao.get_number_of_messages(i, 1))
    data[i].append(data[i][1] + data[i][2])

data_df = pd.DataFrame([
    {"Категория": CANDIDATE_LABELS[i].capitalize(),
     # "Неоценено": "‐" if data[i][3] == 0 else f"{round(data[i][0]/data[i][3]*100,2)}%",
     "👎 Неполезно": "‐" if data[i][3] == 0 else f"{round(data[i][1]/data[i][3]*100,2)}%",
     "👍 Полезно": "‐" if data[i][3] == 0 else f"{round(data[i][2]/data[i][3]*100,2)}%",
     "Всего": data[i][3]}
    for i in range(4)
]
)

st.dataframe(
    data_df,
    hide_index=True,
)
