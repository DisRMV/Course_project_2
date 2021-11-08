import vk as v
import db
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


my_token_g = db.get_data()['Group_token']
my_token_a = db.get_data()['Admin_token']


def main():
    bot = v.Group(my_token_g)
    admin = v.Admin(my_token_a)
    con = db.create_database('db_vk')

    # Создание кнопки
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Поиск кандидатов', color=VkKeyboardColor.SECONDARY)

    while True:
        elimination_id = db.select_user_id(con)
        user_id = bot.listen()[0]
        bot.send_message(user_id, 'Для начала поиска нажмите на кнопку "Поиск кандидатов"',
                         keyboard=keyboard.get_keyboard())
        if bot.listen()[1] == 'Поиск кандидатов':
            user_info = bot.get_info(user_id)
            search_term = bot.data_checking(user_info)
            search_result = admin.user_search(search_term, elimination_id)
            top_photos_of_result_users = admin.top_photo(search_result)
            db.insert_data(con, top_photos_of_result_users)
            bot.show_photo(data_to_send=top_photos_of_result_users, user_id=user_id)
        else:
            bot.send_message(user_id, f'Я умею только искать, так что жми кнопку поиск')


if __name__ == '__main__':
    main()
