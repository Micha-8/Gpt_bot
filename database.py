import sqlite3

DB_NAME = 'info.db'
DB_TABLE_USERS_NAME = 'users'


def execute_query(db_file, query, data=None):
    connection = None  # Определение переменной connection

    try:
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

        connection.commit()

        rows = cursor.fetchall()  # Получение результатов запроса
        return rows  # Возвращение результатов запроса

    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса:", e)

    finally:
        if connection:
            connection.close()


def create_db(database_name=DB_NAME):
    db_path = f'{database_name}'
    connection = sqlite3.connect(db_path)
    connection.close()


def create_table(table_name):
    sql_query = f'CREATE TABLE IF NOT EXISTS {table_name} ' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INTEGER, ' \
                f'subject TEXT, ' \
                f'level TEXT, ' \
                f'task TEXT, ' \
                f'answer TEXT)'
    execute_query(sql_query)


def add_user(db_file, user_id, subject, level, task, answer):
    query = '''INSERT INTO users (user_id, subject, level, task, answer) VALUES(?, ?, ?, ?, ?)'''
    data = (user_id, subject, level, task, answer)
    execute_query(db_file, query, data)


def update_subject(db_file, user_id, subject, ):
    query = '''UPDATE users 
               SET  subject = ?
               WHERE user_id = ?
               '''
    data = (subject, user_id)
    execute_query(db_file, query, data)


def update_level(db_file, user_id, level):
    query = '''UPDATE users 
               SET  level = ?
               WHERE user_id = ?
               '''
    data = (level, user_id)
    execute_query(db_file, query, data)


def update_answer(db_file, user_id, answer):
    query = '''UPDATE users 
               SET  answer = ?
               WHERE user_id = ?
               '''
    data = (answer, user_id)
    execute_query(db_file, query, data)


def update_task(db_file, user_id, task):
    query = '''UPDATE users 
               SET  task = ?
               WHERE user_id = ?
               '''
    data = (task, user_id)
    execute_query(db_file, query, data)


def prepare_db(clean_if_exists=False):
    create_db()
    create_table(DB_TABLE_USERS_NAME)
