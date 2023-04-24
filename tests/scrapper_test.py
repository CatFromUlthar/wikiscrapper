import unittest
from scrapper import *
from io import StringIO
from unittest.mock import patch


class ScrapperTest(unittest.TestCase):
    BASE_LINK = 'https://ru.wikipedia.org/wiki/%D0%A4%D0%B5%D0%B2%D1%80%D0%B0%D0%BB%D1%8C%D1%81%D0%BA%D0%B0%D1%8F_%D0%BB%D0%B0%D0%B7%D1%83%D1%80%D1%8C'

    def test_get_raw_txt(self):
        self.assertIsInstance(get_raw_txt(self.__class__.BASE_LINK), BeautifulSoup)

    def test_get_title(self):
        self.assertEqual(get_title(get_raw_txt(self.__class__.BASE_LINK)), 'Февральская лазурь')

    def test_get_shortened_info(self):
        self.assertIsInstance(get_raw_shortened_info(get_raw_txt(self.__class__.BASE_LINK)), str)

    def test_get_last_changed(self):
        self.assertIsInstance(get_last_changed(get_raw_txt(self.__class__.BASE_LINK)), str)


if __name__ == '__main__':
    unittest.main()
