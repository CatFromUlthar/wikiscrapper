import sqlite3


# Записывает полученную информацию в БД
def add_to_database(db_name: str, recompiled_data: dict) -> None:
    try:
        with sqlite3.connect(db_name) as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS articles (
            url TEXT,
            title TEXT,
            shortened_info TEXT,
            last_changed TEXT,
            published TEXT,
            language TEXT
            )""")
            cur.execute("""INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?)""", (
                recompiled_data['url'], recompiled_data['title'], recompiled_data['shortened_info'],
                recompiled_data['last_changed'], recompiled_data['published'], recompiled_data['language']))
            print('Статья записана в БД')
    except Exception as e:
        raise ConnectionError(f'Не удалось выполнить взаимодействие с БД, статья не записана. Ошибка:{e}')
