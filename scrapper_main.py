from scrapper_requester import *
from scrapper_database_interactor import add_to_database


# Главная функция. Активирует все остальные функции в нужной последовательности
def scrap_article(link: str, db: str = 'wiki.db') -> None:
    check_access(link)
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


if __name__ == '__main__':
    scrap_article('https://en.wikipedia.org/wiki/bread')
