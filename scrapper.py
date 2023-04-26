import re

import requests
import unicodedata
from bs4 import BeautifulSoup
import sqlite3
import json
from warnings import warn


# Главная функция. Активирует все остальные функции в нужной последовательности
def scrap_article(link: str, db: str = 'wiki.db') -> None:
    raw_txt = get_raw_txt(link)
    title = get_title(raw_txt)
    raw_shortened_info = get_raw_shortened_info(raw_txt)
    no_unicode = clean_unicode(raw_shortened_info)
    shortened_info = clean_references(no_unicode)
    last_changed = get_last_changed(raw_txt)
    published = get_published(raw_txt)
    language = get_language(raw_txt)
    recompiled_data = recompile(link, title, shortened_info, last_changed, published, language)
    add_to_database(db, recompiled_data)


def check_access(link: str) -> None:
    server_responce = requests.get(link).status_code
    if server_responce == 404:
        raise ConnectionError('Такая страница не существует (404)')
    elif server_responce == 401:
        raise ConnectionError('Требуется авторизация (401)')
    elif server_responce == 403:
        raise ConnectionError('Нет прав доступа (403)')
    elif server_responce in range (500-600):
        raise ConnectionError(f'Ошибка сервера ({server_responce})')


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
def get_last_changed(raw_txt: BeautifulSoup) -> str | None:
    try:
        data = json.loads(raw_txt.find('script', type='application/ld+json').text)['dateModified']
        last_changed = re.sub('T', ' ', data)[0:-1]
        return last_changed
    except KeyError:
        warn('! Не удалось найти дату последнего изменения !')
        return None


# Возвращает дату и время создания страницы
def get_published(raw_txt: BeautifulSoup) -> str | None:
    try:
        data = json.loads(raw_txt.find('script', type='application/ld+json').text)['datePublished']
        published = re.sub('T', ' ', data)[0:-1]
        return published
    except KeyError:
        warn('! Не удалось найти дату создания статьи !')
        return None


# Возвращает язык статьи
def get_language(raw_txt: BeautifulSoup) -> str | None:
    try:
        data = raw_txt.find('script').text
        data_encoded = data[
                       data.index(re.findall("RLCONF", data)[0]) + 7:data.index(re.findall("RLSTATE", data)[0]) - 1]
        language = json.loads(data_encoded)['wgVisualEditor']['pageLanguageCode']
        return language
    except KeyError:
        warn('! Не удалось найти язык статьи !')
        return None


# Возвращает словарь, скомпилированный из полученной информации
def recompile(link: str, title: str, shortened_info: str, last_changed: str, published: str, language: str) -> dict:
    recompiled_data = (
        dict(url=link, title=title, shortened_info=shortened_info, last_changed=last_changed, published=published,
             language=language))
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


if __name__ == '__main__':
    check_access('https://ru.wikipedia.org/wiki/Sssss')
