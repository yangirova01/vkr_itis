import pandas as pd
from typing import List, Optional
import vk_api
from dataclasses import dataclass

def parse_posts(posts: dict) -> pd.DataFrame:
    """Parse posts from VK API response to DataFrame.
    """
    data = []
    for post in posts['items']:
        row = {'text': post.get('text', '')}
        for field in ['likes', 'reposts', 'comments', 'views']:
            row[field] = post.get(field, {}).get('count', 0)
            if not isinstance(row[field], int):
                row[field] = 0
                print(f"Error: invalid '{field}' field in post {post}")
        data.append(row)

    return pd.DataFrame(data)

def get_comments(posts, vk, user_input):
    df = pd.DataFrame(columns=['id_post', 'text'])
    for post in posts['items']:
        comments = vk.wall.getComments(owner_id=user_input, post_id=post.get('id'), count=100).get('items', [])
        text = ' '.join([comment.get('text', '') for comment in comments])
        df = df.append({'id_post': post.get('id'), 'text': text}, ignore_index=True)

    return df

def get_members(vk, user_input, all_members=False, limit=3500):
    first = vk.groups.getMembers(group_id=user_input).get('items', [])
    members = vk.groups.getMembers(group_id=user_input)
    members = members['count']
    data = first
    if all_members:
        count = members//limit
        for i in range(1, count+1):
            data = data + vk.groups.getMembers(group_id=user_input,offset=i*limit).get('items', [])
        return data
    else:
        offset = limit
        data = data + vk.groups.getMembers(group_id=user_input,offset=offset).get('items', [])
        return data


@dataclass
class UserData:
    user_id: int
    bdate: Optional[str]
    sex: Optional[int]
    city: Optional[str]

def get_user_data(vk: vk_api.VkApi, member: int) -> Optional[UserData]:
    try:
        user_data = vk.users.get(user_ids=member, fields='bdate,sex,city')[0]
        return UserData(user_data['id'], user_data.get('bdate'), user_data.get('sex'), user_data.get('city', {}).get('title'))
    except:
        return None

def get_user_data_list(vk: vk_api.VkApi, members: List[int]) -> List[UserData]:
    user_data_list = []
    for member in members:
        user_data = get_user_data(vk, member)
        if user_data is not None:
            user_data_list.append(user_data)
    return user_data_list

def get_members(vk, user_input, all_members=False, limit=3500):
    first = vk.groups.getMembers(group_id=user_input).get('items', [])
    members = vk.groups.getMembers(group_id=user_input)
    members = members['count']
    data = first
    if all_members:
        count = members//limit
        for i in range(1, count+1):
            data = data + vk.groups.getMembers(group_id=user_input,offset=i*limit).get('items', [])
        return data
    else:
        offset = limit
        data = data + vk.groups.getMembers(group_id=user_input,offset=offset).get('items', [])
        return data
