import pandas as pd
import streamlit as st
from datetime import datetime
from dataframes import parse_posts, get_comments, get_members


def create_age_group(age):
    age = int(age)
    current_year = datetime.now().year
    age = current_year - age

    age_groups = {
        range(0, 14): 'No year',
        range(14, 18): '14-18',
        range(18, 25): '18-25',
        range(25, 30): '25-30',
        range(30, 35): '30-35',
        range(35, 40): '35-40',
        range(40, 45): '40-45',
        range(45, 50): '45-50',
        range(50, 55): '50-55',
        range(55, 60): '55-60',
        range(60, 65): '60-65',
        range(65, 200): '65+'
    }

    for age_range, age_group in age_groups.items():
        if age in age_range:
            return age_group

def map_sex(sex: int):
    if sex == 1:
        return "Женский"
    else:
        return "Мужской"






def process_member_profiles(members, count_members, vk):
    hidden_profile_count = 0
    id_hidden = []
    name_hidden = []
    surname_hidden = []
    members_df = pd.DataFrame(columns=['id', 'имя', 'фамилия', 'год', 'пол', 'город', 'название группы', 'возраст-группа'])

    for i, m in enumerate(members[:int(count_members)]):
        try:
            row = vk.users.get(user_ids=m, fields='bdate,sex,city', lang='ru')
            id = row[0]['id']
            name = row[0]['first_name']
            surname = row[0]['last_name']
            bdate = row[0]['bdate']
            sex = row[0]['sex']
            city = row[0]['city']['title']

            sex = map_sex(int(sex))
            year = bdate.split('.')[-1]
            if len(year) != 4:
                year = 'No year'

            age_group = create_age_group(int(year))

            user_items = vk.users.getSubscriptions(user_id=m, extended=1)['items']
            group_names = [item['name'] for item in user_items]

            members_df = members_df.append({
                'id': id,
                'имя': name,
                'фамилия': surname,
                'год': year,
                'пол': sex,
                'город': city,
                'название группы': group_names,
                'возраст-группа': age_group
            }, ignore_index=True)

        except:
            id_hidden.append(id)
            name_hidden.append(name)
            surname_hidden.append(surname)
            hidden_profile_count += 1

    members_df = members_df.reset_index(drop=True)
    members_df.index += 1

    return members_df, hidden_profile_count, id_hidden, name_hidden, surname_hidden
