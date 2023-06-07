import streamlit as st
import pandas as pd


def load_data():
    text_file = st.sidebar.file_uploader("Загрузите текстовый файл",type=["txt", "csv"])
    if text_file is None:
        st.sidebar.warning("No file uploaded.")

    else:
        try:
            df = pd.read_csv(text_file)
        except ValueError:
            st.sidebar.error(
               "Неверный файл. Пожалуйста, загрузите текстовый файл.")

def save_dataframe(posts: pd.DataFrame, group_name: str, type_file: str):
    """Save DataFrame to file.
    """
    if type_file == "csv":
        posts.to_csv(f"{group_name}.csv", index=False)
    elif type_file in ("xlsx", "xls"):
        posts.to_excel(f"{group_name}.xlsx", index=False)
    else:
        raise ValueError("Неверный тип файла.")

    st.write("Посты успешно получены.")

#load multiple files streamlit

def load_multiple():
    uploaded_files = st.sidebar.file_uploader("Загрузите текстовый файл",type=["txt", "csv"], accept_multiple_files=True)
    list_of_files = []
    if uploaded_files is None:
        st.sidebar.warning("No file uploaded.")
    else:
        for file in uploaded_files:
            try:
                df = pd.read_csv(file)
                list_of_files.append(df)
            except ValueError:
                st.sidebar.error(
                    "Неверный файл. Пожалуйста, загрузите текстовый файл.")

    return list_of_files
