import requests
import unicodedata
from bs4 import BeautifulSoup
import sqlite3
from pympler import asizeof


class ScrappedArticle:
    __slots__ = ('_url', '_raw_txt', '_recompiled_data')

    def __init__(self, url: str):
        self.url = url
        self.raw_txt = BeautifulSoup(requests.get(f'{self._url}').text, 'lxml')
        self.recompiled_data = None

    def __repr__(self):
        return f'ScrappedArticle(url={self._url}, raw_txt={self._raw_txt}, recompiled_data={self._recompiled_data})'

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        if type(value) != str:
            raise AttributeError('url must be string')
        self._url = value

    @property
    def raw_txt(self):
        return self._raw_txt

    @raw_txt.setter
    def raw_txt(self, value):
        self._raw_txt = value

    @property
    def recompiled_data(self):
        return self._recompiled_data

    @recompiled_data.setter
    def recompiled_data(self, value):
        if value is not None:
            print('data has already been recompiled')
        self._recompiled_data = value

    def recompile(self) -> dict:
        url = self._url
        title = self._raw_txt.find('h1', id='firstHeading', string=True).string
        shortened_info = unicodedata.normalize('NFKD',
                                               ' '.join([i.text[0:-1] for i in self._raw_txt.find_all('p', limit=2)]))
        last_changed = self._raw_txt.find('li', id='footer-info-lastmod').text.replace(
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
                self._recompiled_data['url'], self._recompiled_data['title'], self._recompiled_data['shortened_info'],
                self._recompiled_data['last_changed']))


if __name__ == '__main__':
    a1 = ScrappedArticle(
        'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%B3')
    print(a1.recompile())
    print(asizeof.asizeof(a1))
