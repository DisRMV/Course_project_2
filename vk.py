from datetime import datetime
import random
import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


class Admin:

    def __init__(self, token):
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)

    # Ищем 10 пользователей с подходящими условиями. Возвращаем id пользователя и ссылку на профиль
    def user_search(self, user_info, elimination_id):
        sex = user_info['sex']
        hometown = user_info['city']
        status = 1
        age_from = user_info['age_from']
        age_to = user_info['age_to']
        user_search = self.vk.method('users.search', {
            'count': 1000, 'hometown': hometown,
            'sex': sex, 'status': status,
            'age_from': age_from, 'age_to': age_to,
            'fields': 'is_closed'
        })
        time.sleep(0.27)
        address_list = []
        for i in user_search['items']:
            address_dict = {}
            if i['can_access_closed'] and len(address_list) < 10:
                if i['id'] not in elimination_id:
                    address_dict[i['id']] = 'https://vk.com/id' + str(i['id'])
                    address_list.append(address_dict)
        return address_list

    # Получаем топ-3 фотографии подходящих пользователей
    def top_photo(self, list_candidates):
        for i in list_candidates:
            # Получаем список фото пользователя
            uid = i.keys()
            top_3_photo = self.vk.method('photos.getAll', {'owner_id': uid, 'album_id': 'profile', 'extended': 1})
            time.sleep(0.27)
            # Создаем список лайков и сортируем по убыванию
            likes_list = []
            for likes_i in top_3_photo['items']:
                likes_list.append(likes_i['likes']['count'])
            likes_list.sort(reverse=True)
            # Получаем три ссылки на фото с наибольшим кол-вом лайков
            list_url_photo = []
            for photo_i in top_3_photo['items']:
                if photo_i['likes']['count'] in likes_list[0: 3]:
                    list_url_photo.append({photo_i['id']: photo_i['sizes'][-1]['url']})
            i['url_photo'] = list_url_photo
        return list_candidates


class Group:

    def __init__(self, token):
        self.token = token
        self.vk = vk_api.VkApi(token=self.token)
        self.longpol = VkLongPoll(self.vk)
        self.mess_id = self.listen()[0]

    # Слушаем сервер
    def listen(self):
        for event in self.longpol.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    return int(event.user_id), event.text

    # Отправка сообщений
    def send_message(self, user_id, text, keyboard=None, template=None):
        self.vk.method('messages.send', {'user_id': user_id, 'message': text,
                                         'random_id': random.randrange(10 ** 7),
                                         'keyboard': keyboard, 'template': template})

    # Отправка файла
    def send_message_media(self, user_id, media):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'random_id': random.randrange(10 ** 7),
                                         'attachment': media})

    # Получаем информацию о пользователе
    def get_info(self, user_id):
        result = self.vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate, city, relation, sex'})
        user_info = {}
        # возраст
        age = result[0].get('bdate')
        if age is not None and len(age.split('.')) == 3:
            year_birth = datetime.strptime(age, '%d.%m.%Y').year
            this_year = datetime.now().year
            user_info['age_from'] = this_year - year_birth - 2
            user_info['age_to'] = this_year - year_birth + 2
        else:
            user_info['age_from'] = None
            user_info['age_to'] = None
        # пол
        sex = result[0].get('sex')
        if sex == 1:
            sex = 2
        elif sex == 2:
            sex = 1
        else:
            sex = None
        user_info['sex'] = sex
        # город
        city = result[0].get('city')
        if city is not None:
            user_info['city'] = city.get('title')
        else:
            user_info['city'] = None
        return user_info

    # Запрашиваем недостающую информацию
    def data_checking(self, user_info):
        # возраст
        if user_info['age_from'] is None and user_info['age_to'] is None:
            self.send_message(self.mess_id, f'Не хватает данных для поиска. Введите свой возраст')
            receive_message = self.listen()
            user_info['age_from'] = int(receive_message[1]) - 2
            user_info['age_to'] = int(receive_message[1]) + 2

        # пол
        if user_info['sex'] is None:
            self.send_message(self.mess_id, f'''Укажите пол для поиска. 
                                                Отправьте в ответ одну из цифр: 1 - женский, 2 - мужской''')
            receive_message = self.listen()
            user_info['sex'] = int(receive_message[1])

        # город
        if user_info['age_to'] is None:
            self.send_message(self.mess_id, f'Укажите город для поиска. Введите название города.')
            receive_message = self.listen()
            user_info['city'] = receive_message[1]
        return user_info

    # Итоговая отправка результатов поиска пользователю
    def show_photo(self, data_to_send, user_id):
        for user in data_to_send:
            uid, url = user.items()
            show_can = self.vk.method('users.get', {'user_ids': uid[0], 'fields': 'bdate, city, relation, sex'})
            first_name = show_can[0].get('first_name')
            last_name = show_can[0].get('last_name')
            self.send_message(user_id, f'{first_name} {last_name}')
            self.send_message(user_id, uid[1])
            for media in url[1][0:3]:
                photo_url = list(media.items())
                self.send_message_media(user_id, f'photo{uid[0]}_{photo_url[0][0]}')
            time.sleep(1)
        self.send_message(user_id, 'Поиск окончен')
