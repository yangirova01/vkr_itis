import pandas as pd
import requests
import streamlit as st
import vk_api
# datetime
from datetime import datetime
from transliterate import translit
from utils import load_data,load_multiple
from dataframes import parse_posts, get_comments, get_members, get_user_data,get_user_data_list
from pySankey.sankey import sankey
import numpy as np
from Analyzer import process_member_profiles, map_sex, create_age_group
import itertools


import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt


def extract_year(date):
    if date is None:
        return "No year"
    elif len(date.split('.')) == 3:
        return date.split('.')[-1]
    else:
        return "No year"


def extract_data(row):
    id = row[0]['id']
    name = row[0]['first_name']
    surname = row[0]['last_name']
    bdate = row[0]['bdate']
    sex = row[0]['sex']
    city = row[0]['city']['title']
    year = bdate.split('.')[-1]
    if len(year) != 4:
        year = 0

    age_group = create_age_group(int(year))

    data = {
        'id': id,
        'имя': name,
        'фамилия': surname,
        'год': extract_year(bdate),
        'пол': map_sex(sex),
        'город': row[0]['city']['title'],
        'возраст-группа': age_group
    }

    return data


def extract_group_names(members_df=None):
    all_group_names = members_df['название группы'].tolist()
    all_group_names = [item for sublist in all_group_names for item in sublist]
    all_group_names = list(set(all_group_names))
    return all_group_names

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


if 'button_1' not in st.session_state:
    st.session_state.button_1 = False

def cb1():
    st.session_state.button_1 = True
#
#


def generate_sankey_plot(sankey_data, name_col):
    if len(sankey_data) == 0:
        st.write("Нет общих групп")
    else:
        try:
            sankey(sankey_data[name_col + '1'], sankey_data[name_col + '2'])

            # Get current figure
            fig = plt.gcf()

            # Set size in inches
            fig.set_size_inches(6, 6)

            # Set the color of the background to white
            fig.set_facecolor("w")

            # Save the figure
            fig.savefig("customers-goods.png", bbox_inches="tight", dpi=150)

            # Show the figure
            st.pyplot(fig)
        except Exception as e:
            st.write(e)
            pass



def main():


    ########################################## SIDEBAR ##########################################

    with st.sidebar:
        # token = st.text_input("Введите токен:", value="eb6f7172eb6f7172eb6f7172c3e87c58deeeb6feb6f71728f779a0e7ad8e8fc1fd617f2")
        token = st.text_input("Введите токен:",
                              value="2ff60f692ff60f692ff60f695e2ce4eed822ff62ff60f694c094cb35bc606f13492ff84")
        # count = st.text_input("Введите количество постов:", value=100)
        count_members = st.text_input("Введите количество участников:", value=50)
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()


        user_input = st.text_input("Введите ссылку на группу:", value="https://vk.com/club1")


    ########################################## MAIN ##########################################
    hidden_profiles_df = pd.DataFrame(
        columns=['User ID', 'Exception', 'Data', 'Group Names'])

    hidden_profile_count = 0
    if st.sidebar.button("Получить посты"):
        with st.spinner('Получаем посты...'):
            user_input = resolve_url(user_input, vk)
            members = get_members(vk, user_input)
            members = members[:int(count_members)]
            data_df = pd.DataFrame()

            for ind, m in enumerate(members):
                try:
                    # Fetch user data
                    row = vk.users.get(user_ids=m, fields='bdate,sex,city',
                                       lang='ru')
                    user_items = \
                    vk.users.getSubscriptions(user_id=m, extended=1)['items']

                    # Extract data
                    data = extract_data(row)
                    group_names = [item['name'] for item in user_items]
                    data['название группы'] = group_names

                    data_df = data_df.append(data, ignore_index=True)

                except Exception as e:
                    hidden_profile_count += 1
                    hidden_profiles_df = hidden_profiles_df.append({
                        'User ID': m,
                        'Exception': str(e),
                        'Data': data if 'data' in locals() else None,
                        'Group Names': group_names if 'group_names' in locals() else None
                    }, ignore_index=True)
                    continue

            data_df['cсылка'] = 'https://vk.com/id' + data_df['id'].astype(str)
            data_df = data_df[['cсылка', 'имя', 'фамилия', 'год', 'пол', 'город', 'возраст-группа', 'название группы', 'id']]
            #start index from 1
            data_df.index = np.arange(1, len(data_df) + 1)
            st.write(data_df)
            st.write(f"Количество скрытых профилей: {hidden_profile_count}")
            st.write(f"Количество участников: {len(members)}")
            st.write(
                f"Процент скрытых профилей: {round(hidden_profile_count / len(members) * 100, 2)}%")

            # Show dataframe with hidden profiles and exceptions
            st.write("Скрытые профили:")

            hidden_profiles_df['cсылка'] = 'https://vk.com/id' + hidden_profiles_df['User ID'].astype(str)
            hidden_profiles_df = hidden_profiles_df[['cсылка', 'Group Names']]
            #rename columns
            hidden_profiles_df.columns = ['cсылка', 'название группы']


            st.write(hidden_profiles_df)



            ################## GENERATE GROUPS NAMES ##################


            data_df['ФИО'] = data_df['имя'] + ' ' + data_df['фамилия']
            data_df = data_df[['id', 'ФИО', 'название группы']]
            data_df = data_df.explode('название группы')


            ################## CREATE DATA FOR PLOT ##################
            group_col = 'название общей группы'
            name_col = 'ФИО'
            id_col = 'id'


            sankey_data = pd.DataFrame(
                columns=[name_col + '1', name_col + '2', group_col])

            for i, member1 in data_df.iterrows():
                for j, member2 in data_df.iloc[i + 1:].iterrows():
                    if member1[id_col] != member2[id_col]:
                        if member1['название группы'] == member2[
                            'название группы']:
                            sankey_data = sankey_data.append(
                                [{name_col + '1': member1[name_col],
                                  name_col + '2': member2[name_col],
                                  group_col: member1['название группы']}])

            sankey_data.index = list(range(1, len(sankey_data) + 1))
            st.write("Общие группы для каждой пары пользователей")
            st.dataframe(sankey_data)


            ################## SANKEY PLOT ##################
            st.write("Схема общих групп")
            generate_sankey_plot(sankey_data, name_col)


            #### SAVE  DATA for GRAPH####

            csv = convert_df(sankey_data)
            st.sidebar.download_button(
                label="Скачать данные для графа - используйте их в вкладке graph dynamic - это входные данные для графа - data.csv",
                data=csv,
                file_name='data.csv',
                mime='text/csv',
            )
















if __name__ == '__main__':
    main()

