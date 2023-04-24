import re

import requests
import unicodedata
from bs4 import BeautifulSoup
import sqlite3


# Главная функция. Активирует все остальные функции в нужной последовательности
def scrap_article(link: str) -> None:
    raw_txt = get_raw_txt(link)
    title = get_title(raw_txt)
    raw_shortened_info = get_raw_shortened_info(raw_txt)
    no_unicode = clean_unicode(raw_shortened_info)
    shortened_info = clean_references(no_unicode)
    last_changed = get_last_changed(raw_txt)
    recompiled_data = recompile(link, title, shortened_info, last_changed)
    add_to_database('wiki.db', recompiled_data)


# Возвращает HTML-код со страницы википедии
def get_raw_txt(link: str) -> BeautifulSoup:
    try:
        raw_txt = BeautifulSoup(requests.get(f'{link}').text, 'lxml')
        return raw_txt
    except Exception as e:
        raise ConnectionError(f'Не удалось получить данные с сайта. Ошибка: {e}')


# Возвращает заголовок статьи из HTML-кода
def get_title(raw_txt: BeautifulSoup) -> str:
    title = raw_txt.find('h1', id='firstHeading', string=True).string
    return title


# Возвращает текст первых 2 абзацев вступления статьи (краткая информация)
def get_raw_shortened_info(raw_txt: BeautifulSoup) -> str:
    all_txt = raw_txt.find_all('p', limit=2)
    txt_list = [i.text[0:-1] for i in all_txt]
    raw_shortened_info = ''.join(txt_list)
    return raw_shortened_info


# Убирает юникод-символы из краткой информации
def clean_unicode(raw_shortened_info) -> str:
    no_unicode = unicodedata.normalize('NFKD', raw_shortened_info)
    return no_unicode


# Убирает остатки ссылок из краткой информации
def clean_references(no_unicode) -> str:
    pattern = r'\[\d+\]'
    shortened_info = re.sub(pattern, '', no_unicode)
    return shortened_info


# Возвращает дату и время последнего изменения страницы
def get_last_changed(raw_txt: BeautifulSoup) -> str:
    last_changed = raw_txt.find('li', id='footer-info-lastmod').text.replace(
        ' Эта страница в последний раз была отредактирована ', '')[:-1]
    return last_changed


# Возвращает словарь, скомпилированный из полученной информации
def recompile(link: str, title: str, shortened_info: str, last_changed: str) -> dict:
    recompiled_data = (dict(url=link, title=title, shortened_info=shortened_info, last_changed=last_changed))
    return recompiled_data


# Записывает полученную информацию в БД
def add_to_database(db_name: str, recompiled_data: dict) -> None:
    try:
        with sqlite3.connect(db_name) as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS articles (
            url TEXT,
            title TEXT,
            shortened_info TEXT,
            last_changed TEXT
            )""")
            cur.execute("""INSERT INTO articles VALUES (?, ?, ?, ?)""", (
                recompiled_data['url'], recompiled_data['title'], recompiled_data['shortened_info'],
                recompiled_data['last_changed']))
            print('Статья записана в БД')
    except Exception as e:
        raise ConnectionError(f'Не удалось выполнить взаимодействие с БД, статья не записана. Ошибка:{e}')


if __name__ == '__main__':
    scrap_article(
        'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D0%B2%D1%80%D0%B0%D0%BB%D1%8C%D1%81%D0%BA%D0%B0%D1%8F_%D0%BB%D0%B0%D0%B7%D1%83%D1%80%D1%8C')
