import requests
import unicodedata
from bs4 import BeautifulSoup
import sqlite3


class ScrappedArticle:

    def __init__(self, url: str):
        self.url = url
        self.raw_txt = BeautifulSoup(requests.get(f'{self.url}').text, 'lxml')
        self.recompiled_data = None

    def __repr__(self):
        return f'ScrappedArticle(url={self.url}, raw_txt={self.raw_txt}, recompiled_data={self.recompiled_data})'

    def recompile(self) -> dict:
        url = self.url
        title = self.raw_txt.find('h1', id='firstHeading', string=True).string
        shortened_info = unicodedata.normalize('NFKD',
                                               ' '.join([i.text[0:-1] for i in self.raw_txt.find_all('p', limit=2)]))
        last_changed = self.raw_txt.find('li', id='footer-info-lastmod').text.replace(
            ' Эта страница в последний раз была отредактирована ', '')[:-1]
        self.recompiled_data = dict(url=url, title=title, shortened_info=shortened_info, last_changed=last_changed)
        return self.recompiled_data

    def add_to_db(self):
        with sqlite3.connect('wiki.db') as con:
            cur = con.cursor()

            cur.execute("""CREATE TABLE IF NOT EXISTS articles (
            url TEXT,
            title TEXT,
            shortened_info TEXT,
            last_changed TEXT
            )""")
            cur.execute("""INSERT INTO articles VALUES (?, ?, ?, ?)""", (
            self.recompiled_data['url'], self.recompiled_data['title'], self.recompiled_data['shortened_info'],
            self.recompiled_data['last_changed']))


if __name__ == '__main__':
    a1 = ScrappedArticle(
        'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B3')
    print(a1.recompile())
    a1.add_to_db()
