import requests
import unicodedata
from bs4 import BeautifulSoup
import sqlite3


class ScrappedArticle:

    def __init__(self, url: str):
        self.url = url
        self.raw_txt = BeautifulSoup(requests.get(f'{self.url}').text, 'lxml')

    def __repr__(self):
        return f'ScrappedArticle(url={self.url}, raw_txt={self.raw_txt})'

    def recompile(self):
        shortened_info = unicodedata.normalize('NFKD',
                                               ' '.join([i.text[0:-1] for i in self.raw_txt.find_all('p', limit=2)]))
        print(shortened_info)
        recompiled_data = dict(url=self.url, title=self.raw_txt.find('h1', id='firstHeading', string=True).string,
                               shortened_info=unicodedata.normalize('NFKD', self.raw_txt.find('p').text)[:-2],
                               last_changed=self.raw_txt.find('li', id='footer-info-lastmod').text.replace(
                                   ' Эта страница в последний раз была отредактирована ', '')[:-1])
        return recompiled_data



if __name__ == '__main__':
    a1 = ScrappedArticle(
        'https://ru.wikipedia.org/wiki/%D0%9A%D1%83%D0%B4%D0%B5%D0%BB%D0%BA%D0%B0,_%D0%A0%D0%BE%D0%BB%D0%B0%D0%BD%D0%B4')
    print(a1.recompile())
