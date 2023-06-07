import pandas as pd
import requests
import streamlit as st
import vk_api
from collections import Counter
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# datetime
import datetime
from transliterate import translit
# from utils import load_data,load_multiple
from dataframes import parse_posts, get_comments, get_members, get_user_data,get_user_data_list
from pySankey.sankey import sankey
import numpy as npxw
import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt

import re
import fasttext
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
from dataframes import parse_posts, get_comments, get_members

from dictionary_profanity_filter import ProfanityFilter

pf = ProfanityFilter()


fasttext.FastText.eprint = lambda x: None

FastTextSocialNetworkModel.MODEL_PATH = 'data/models/fasttext-social-network-model.bin'
token = "1de87fc11de87fc11de87fc1ee1efb566d11de81de87fc179d10abdb96a9bbfea467460"

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

def resolve_url(url):
    screen_name = url.split('/')[-1]
    ids = vk.utils.resolveScreenName(screen_name=screen_name)
    return ids['object_id']


with st.sidebar:

    url = st.text_input("Введите ссылку на группу","https://vk.com/club1")
    # count = st.slider("Количество постов", 0, 50000, 100)
    count = st.text_input("Количество постов", 100, 50000, 100)

    if url:
        group_id = resolve_url(url)
        if group_id:
            if str(group_id)[0] != "-":
                user_input_ = "-" + str(group_id)
                posts = vk.wall.get(owner_id=user_input_, count=count)
st.title("Анализ текстов на предмет ненормативной лексики")
posts_df = parse_posts(posts)
st.dataframe(posts_df.rename(columns={"text": "Текст поста","likes": "Количество лайков","comments": "Количество комментариев","reposts": "Количество репостов","views": "Количество просмотров"}))
st.write("Количество постов:", len(posts_df))

regex_string = r"(?iu)\b((у|[нз]а|(хитро|не)?вз?[ыьъ]|с[ьъ]|(и|ра)[зс]ъ?|(о[тб]|под)[ьъ]?|(.\B)+?[оаеи])?-?([её]б(?!о[рй])|и[пб][ае][тц]).*?|(н[иеа]|([дп]|верт)о|ра[зс]|з?а|с(ме)?|о(т|дно)?|апч)?-?ху([яйиеёю]|ли(?!ган)).*?|(в[зы]|(три|два|четыре)жды|(н|сук)а)?-?бл(я(?!(х|ш[кн]|мб)[ауеыио]).*?|[еэ][дт]ь?)|(ра[сз]|[зн]а|[со]|вы?|п(ере|р[оие]|од)|и[зс]ъ?|[ао]т)?п[иеё]зд.*?|(за)?п[ие]д[аое]?р([оа]м|(ас)?(ну.*?|и(ли)?[нщктл]ь?)?|(о(ч[еи])?|ас)?к(ой)|юг)[ауеы]?|манд([ауеыи](л(и[сзщ])?[ауеиы])?|ой|[ао]вошь?(е?к[ауе])?|юк(ов|[ауи])?)|муд([яаио].*?|е?н([ьюия]|ей))|мля([тд]ь)?|лять|([нз]а|по)х|м[ао]л[ао]фь([яию]|[еёо]й))\b"

regex = re.compile(regex_string)

def get_bad_words(text):
    return regex.findall(text)

posts_df['bad_words'] = posts_df['text'].apply(lambda x: get_bad_words(x))
posts_df['bad_words'] = posts_df['bad_words'].apply(lambda x: [list(line) for line in x])
posts_df['bad_words'] = posts_df['bad_words'].apply(lambda x: [item for sublist in x for item in sublist])
posts_df['bad_words'] = posts_df['bad_words'].apply(lambda x: [item for item in x if item != ''])


posts_df['all_words'] = posts_df['text'].apply(lambda x: x.split())
# posts_df['all_words'] = posts_df['all_words'].apply(lambda x: [item for sublist in x for item in sublist])
# posts_df['all_words'] = posts_df['all_words'].apply(lambda x: [item for item in x if item != ''])

# st.write(posts_df['all_words'])

all_words = posts_df['all_words'].tolist()
all_words = [item for sublist in all_words for item in sublist]
all_words = [item for item in all_words if item != '']
all_words = [item for item in all_words if len(item) > 2]

blocked_words = ['https', 'http', 'vk', "API"]
all_words = [item for item in all_words if item not in blocked_words]



temp = posts_df[posts_df['bad_words'].apply(lambda x: len(x) > 0)]
if len(temp) > 0:
    st.dataframe(temp.rename(columns={"text": "Текст поста","likes": "Количество лайков","comments": "Количество комментариев","reposts": "Количество репостов","views": "Количество просмотров"}))
else:
    st.write("Нет постов с матами")

st.markdown("## Маты в комментариях")

comments = get_comments(posts, vk, -group_id)
comments_df = pd.DataFrame(comments)
comments_df['bad_words'] = comments_df['text'].apply(lambda x: get_bad_words(x))
comments_df['bad_words'] = comments_df['bad_words'].apply(lambda x: [list(line) for line in x])
comments_df['bad_words'] = comments_df['bad_words'].apply(lambda x: [item for sublist in x for item in sublist])
comments_df['bad_words'] = comments_df['bad_words'].apply(lambda x: [item for item in x if item != ''])


if len(comments_df) > 0:
    #only not empty
    temp = comments_df[comments_df['bad_words'].apply(lambda x: len(x) > 0)]
    temp = temp[['text', 'bad_words']]
    st.dataframe(temp.rename(columns={"text": "Текст комментария", "bad_words": "Маты"}))





    bad_words = [item for sublist in comments['bad_words'].tolist() for item in
                 sublist]
    bad_words = [item for item in bad_words if item != '']
    # lower
    bad_words = [x.lower() for x in bad_words]
    #more than 2 letters
    bad_words = [x for x in bad_words if len(x) > 2]

    cnt = Counter(bad_words)
    # top 10 bad words
    cnt10 = cnt.most_common(10)
    # plot
    fig, ax = plt.subplots(figsize=(10, 5))
    #title
    ax.set_title('Топ 10 матов в комментариях')
    vulgarity = [x[0] for x in cnt10], [x[1] for x in cnt10]
    #sub last 3 letters for *
    censored_list = [x[:-3] + '*' for x in vulgarity[0]]


    ax.bar(censored_list, vulgarity[1])
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("Матов в комментариях нет")


#remove bad words from all words
all_words = [item for item in all_words if item not in  vulgarity[0]]

#remove not needed words
blocked_words = ['https', 'http', 'vk', "API","callback", "Mini", "Apps", "VK"]
all_words = [item for item in all_words if item not in blocked_words]

st.markdown("## Облако часто используемых слов")
wordcloud = WordCloud(background_color='white').generate(' '.join(all_words))
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")
st.pyplot(fig)

# #процент матов в постах в соотношении с общим количеством слов

st.write("Процент матов в постах в соотношении с общим количеством слов")
score = len(bad_words) / len(all_words)*100
score = round(score, 2)
st.write(score, "%")

#сохранение в файл матов side bar
if st.sidebar.button('Сохранить в файл неноцензурную лексику'):
    with open('bad_words.txt', 'w') as f:
        for item in bad_words:
            f.write("%s\n" % item)
    st.sidebar.write("Файл сохранен")



