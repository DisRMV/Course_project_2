import sqlalchemy
import json


def get_data():
    with open('data.json', 'r', encoding='utf-8') as data:
        return json.load(data)


def create_database(db_name):
    postgres = get_data()['Data_base_password']
    localhost = get_data()['Data_base_port']
    try:
        # Создаем базу данных
        engine = sqlalchemy.create_engine(f'postgresql://postgres:{postgres}@localhost:{localhost}/postgres')
        connection = engine.connect()
        connection.execute('commit')
        connection.execute(f'create database {db_name}')
        connection.close()
        # Создаем подключение к созданной базе данных
        engine = sqlalchemy.create_engine(f'postgresql://postgres:{postgres}@localhost:{localhost}/{db_name}')
        connection = engine.connect()
        create_table(connection)
        return connection
    except sqlalchemy.exc.ProgrammingError:
        # Создаем подключение к созданной базе данных
        engine = sqlalchemy.create_engine(f'postgresql://postgres:{postgres}@localhost:{localhost}/{db_name}')
        connection = engine.connect()
        return connection
    except sqlalchemy.exc.OperationalError:
        print('Ошибка подключения к базе данных')


# Создание таблицы
def create_table(base_connection):
    # Таблица id пользователей и их url
    base_connection.execute('''CREATE TABLE IF NOT EXISTS user_id (
    id SERIAL PRIMARY KEY,
    url_id VARCHAR(50) NOT NULL UNIQUE);''')


#  Заполнение таблицы
def insert_data(base_connection, users_info):
    try:
        for user in users_info:
            uid, url = user.items()
            insert = f"INSERT INTO user_id(id, url_id) VALUES('{uid[0]}', '{uid[1]}');"
            base_connection.execute(insert)
    except AttributeError:
        print('Ошибка подключения к базе данных, запись данных не возможна')


# Получение списка id из базы данных
def select_user_id(base_connection):
    list_id = []
    try:
        for i in base_connection.execute('''SELECT id FROM user_id''').fetchall():
            list_id.append(i[0])
        return list_id
    except AttributeError:
        print('Ошибка подключения к базе данных, получение данных из БД не возможно')
        return list_id
