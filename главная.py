import streamlit as st
import pandas as pd
import vk_api
from NLP import PreprocessTransormer
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from dataframes import parse_posts, get_comments, get_members
from dataclasses import dataclass
import matplotlib.pyplot as plt
import nltk
import re
import fasttext
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel

fasttext.FastText.eprint = lambda x: None



from sklearn.pipeline import Pipeline

import warnings
warnings.filterwarnings("ignore")

from st_pages import Page, show_pages, add_page_title
from utils import load_data, save_dataframe


FastTextSocialNetworkModel.MODEL_PATH = 'data/models/fasttext-social-network-model.bin'




@st.cache_data
def convert_df(df=None):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def resolve_url(url, vk):
    screen_name = url.split('/')[-1]
    try:
        ids = vk.utils.resolveScreenName(screen_name=screen_name)
        return ids['object_id']
    except Exception as e:
        print(e)
        return None


st.session_state['df'] = None
st.session_state['posts'] = None
st.session_state['members'] = None
st.session_state['comments'] = None
st.session_state['labels'] = None
st.session_state['group_name'] = None

def main():
    st.set_page_config(layout="wide")
    st.sidebar.title("Анализ текстов на предмет ненормативной лексики")
    st.sidebar.markdown("Это приложение позволяет проанализировать посты, комментарии и участников группы ВКонтакте.")
    #change name of the page
    st.sidebar.title("Выберите страницу")

    with st.sidebar:
        # token = st.text_input("Введите токен:", value="eb6f7172eb6f7172eb6f7172c3e87c58deeeb6feb6f71728f779a0e7ad8e8fc1fd617f2")
        token = st.text_input("Введите токен:",
                              value="2ff60f692ff60f692ff60f695e2ce4eed822ff62ff60f694c094cb35bc606f13492ff84")
        count = st.text_input("Введите количество постов:", value=100)
        # count_members = st.text_input("Введите количество участников:", value=50)
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()


        user_input = st.text_input("Введите ссылку на группу:", value="https://vk.com/enter.media")
        user_input_original = user_input


    if st.sidebar.button("Загрузить данные"):
        if user_input:
            user_input = resolve_url(user_input, vk)


        if str(user_input)[0] != "-":
            user_input_ = "-" + str(user_input)
            posts = vk.wall.get(owner_id=int(user_input_), count=count)


            # ####### PREPARE DATA #######
            #
            group_name = vk.groups.getById(group_id=user_input)
            group_name = group_name[0]['name']
            st.write(f"Название группы: {group_name}")
            st.write(f"ID группы: {user_input}")
            #
            # number of members
            members = vk.groups.getMembers(group_id=user_input)
            members = members['count']
            st.write(f"Количество участников: {members}")

            comments = get_comments(posts, vk, -user_input) # HERE
            originalUrl = str(user_input_original)+ "?w=wall" +"-"+str(user_input)+"_"+str(posts['items'][0]['id'])
            originalUrl_column = [str(user_input_original)+ "?w=wall" +"-"+str(user_input)+"_"+str(posts['items'][i]['id'])
                                    for i in range(len(posts['items']))]
            comments['originalUrl'] = originalUrl_column
            #rename columns
            comments.rename(columns={'originalUrl': 'ссылка'}, inplace=True)



            posts_data = parse_posts(posts) # HERE

            #####  add sentiment to posts #####

            tokenizer = RegexTokenizer()
            model = FastTextSocialNetworkModel(tokenizer=tokenizer)

            posts_data['тональность'] = model.predict(posts_data['text'], k=-1)

            sentiment_df = posts_data['тональность'].apply(pd.Series) # extract positive, negative and neutral sentiment from dict
            sentiment_df = sentiment_df.applymap(lambda x: '{:.2f}%'.format(x * 100)) # convert to percentage
            posts_data = pd.concat([posts_data, sentiment_df], axis=1) # add to original df

            st.write("Таблица с постами")
            posts_data.index = posts_data.index + 1
            posts_data = posts_data[
                ['text', 'likes', 'reposts', 'views', 'comments', 'positive',
                 'negative', 'neutral']]
            st.dataframe(posts_data.rename(
                columns={'text': 'текст', 'likes': 'лайки',
                         'reposts': 'репосты', 'views': 'просмотры',
                         'comments': 'комментарии',
                         'positive': 'положительная тональность',
                         'negative': 'отрицательная тональность',
                         'neutral': 'нейтральная тональность'}))

            csv = convert_df(posts_data.rename(
                columns={'text': 'текст', 'likes': 'лайки',
                         'reposts': 'репосты', 'views': 'просмотры',
                         'comments': 'комментарии',
                         'positive': 'положительная тональность',
                         'negative': 'отрицательная тональность',
                         'neutral': 'нейтральная тональность'}))

            ####### ВСЕ АНАГОГИЧНО ДЛЯ КОММЕНТАРИЕВ #######
            st.write("Таблица с комментариями")

            comments.index = comments.index + 1

            comments['тональность'] = model.predict(comments['text'], k=-1)
            # extract positive, negative and neutral sentiment from dict
            sentiment_df = comments['тональность'].apply(pd.Series)
            sentiment_df = sentiment_df.applymap(
                lambda x: '{:.2f}%'.format(x * 100))
            comments = pd.concat([comments, sentiment_df], axis=1)
            comments.drop(['тональность'], axis=1, inplace=True)
            comments.drop(['skip'], axis=1, inplace=True)
            comments.drop(['speech'], axis=1, inplace=True)
            comments.drop(['id_post'], axis=1, inplace=True)

            st.dataframe(comments.rename(
                columns={'text': 'текст', 'likes': 'лайки',
                         'reposts': 'репосты', 'views': 'просмотры',
                         'comments': 'комментарии',
                         'positive': 'положительная тональность',
                         'negative': 'отрицательная тональность',
                         'neutral': 'нейтральная тональность'}), width=1000)

            csv_comments = convert_df(comments.rename(
                columns={'text': 'текст', 'likes': 'лайки',
                         'reposts': 'репосты', 'views': 'просмотры',
                         'comments': 'комментарии',
                         'positive': 'положительная тональность',
                         'negative': 'отрицательная тональность',
                         'neutral': 'нейтральная тональность'}))


if __name__ == '__main__':


    main()


