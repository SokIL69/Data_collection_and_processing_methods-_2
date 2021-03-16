# Методы сбора и обработки данных из сети Интернет
# Соковнин Игорь Леонидович
#
# Урок 4. Парсинг HTML. XPath
#
# 1. Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# - название источника;
# - наименование новости;
# - ссылку на новость;
# - дата публикации.
#
# 2. Сложить собранные данные в БД

import requests
from lxml import html
from pprint import pprint
from datetime import datetime
from pymongo import MongoClient


# ============================ #
# 1. Собрать новости с сайтов:
# - news.mail.ru,
# - lenta.ru,
# - yandex-новости
# ============================ #

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
news = []


def news_mail_full(link):
    """
    Получить информацио о новости с сайта "https://news.mail.ru/" по ссылке.

    Parameters:
    ----------
    link: string
        Ссылка на новость.

    Returns
    -------
    source: string
        название источника.

    date: string
        дата публикации.

    """
    response = requests.get(link, headers=header)
    dom = html.fromstring(response.text)
    #items = dom.xpath('//div[@class="article js-article js-module"]')
    items = dom.xpath('//div[contains(@class,"article js-article")]')

    for item in items:
        #//div[@class="article js-article js-module"]//span[@class ="link__text"]
        source = item.xpath('.//span[@ class ="link__text"]/text()')[0]  # название источника;
        #//div[@class ="article js-article js-module"]//span[@class ="note__text breadcrumbs__text js-ago"]/@ datetime
        date = item.xpath('//span[@ class ="note__text breadcrumbs__text js-ago"]/@ datetime')[0]
        break

    return source, date


# Тестирование функции
# link = 'https://news.mail.ru/politics/45575316/'
# news_mail_full(link)


def news_mail_main():
    """
    Получить новости со сстраницы "https://news.mail.ru/".

    """
    main_url = 'https://news.mail.ru'
    response = requests.get(main_url, headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath('//a[contains(@class,"photo photo_full photo_scale")] | //a[contains(@class,"photo photo_small photo_scale photo_full js-topnews__item")] ')
    i = 0
    for item in items:
        news_item = {}
        name = item.xpath('.//span[@class="photo__title photo__title_new photo__title_new_hidden js-topnews__notification"]/text()')[0].replace('\xa0', ' ')
        link = item.xpath('//a[contains(@class, "js-topnews__item")]/@href')[i]  # ссылка на новость;

        news_item['name'] = name
        news_item['link'] = link

        source, date = news_mail_full(link)
        news_item['source'] = source
        news_item['date'] = date

        news.append(news_item)
        i += 1

    # pprint(news)


# Получаем главные новости со сстраницы "https://news.mail.ru/".
news_mail_main()


def lenta_news_main():
    """
    Получить главные новости со сстраницы "https://lenta.ru/".

    """
    main_url = 'https://lenta.ru'
    response = requests.get(main_url, headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath('//div[@class="b-yellow-box__wrap"]/div[@class="item"]')
    source = "lenta.ru"

    for item in items:
        news_item = {}
        name = item.xpath('.//a/text()')[0].replace('\xa0', ' ')  # наименование новости;
        link = item.xpath('.//a/@href')[0]  # ссылка на новость;
        day_list = link.replace('/news/', '').split('/')
        day = day_list.pop(0) + '.' + day_list.pop(0) + '.' + day_list.pop(0)

        news_item['name'] = name
        news_item['link'] = main_url + link
        news_item['source'] = source
        news_item['date'] = day
        news.append(news_item)

    # pprint(news)


# Получаем главные новости со страницы "https://lenta.ru/".
lenta_news_main()


def yandex_news_main():
    """
    Получить главные новости с сайта https://yandex.ru/.

    """
    main_url = 'https://yandex.ru/'
    response = requests.get(main_url, headers=header)

    dom = html.fromstring(response.text)
    items = dom.xpath('//ol/li')

    date = datetime.today().strftime("%d-%m-%Y")
    for item in items:
        news_item = {}
        source = item.xpath('.//object/@title')[0]  # название источника;
        name = item.xpath('.//span[contains(@class ,"news__item-content")]/text()')[0]  # наименование новости;
        link = item.xpath('.//a/@href')[0]  # ссылка на новость;

        news_item['source'] = source
        news_item['link'] = link
        news_item['name'] = name
        news_item['date'] = date

        news.append(news_item)

    # pprint(news)


# Получаем главные новости с сайта https://yandex.ru/
def yandex_news():
    """
    Получить новости со сстраницы "https://yandex.ru/news?from=tabbar".

    """
    main_url = 'https://yandex.ru/'
    response = requests.get(main_url + 'news?from=tabbar', headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath('//article')

    date = datetime.today().strftime("%d-%m-%Y")
    for item in items:
        news_item = {}
        name = item.xpath('.//h2[@class="mg-card__title"]/text()')[0].replace('\xa0', ' ') # наименование новости;
        link = item.xpath('.//span/a/@href')[0]  # ссылка на новость;
        now = date + ' ' + item.xpath('.//span[@class ="mg-card-source__time"]/text()')[0]  # название источника;
        source = item.xpath('.//span[@class ="mg-card-source__source"]/a/text()')[0]  # название источника;

        news_item['name'] = name
        news_item['link'] = link
        news_item['date'] = now
        news_item['source'] = source
        news.append(news_item)

    # pprint(news)


# Получаем новости со страницы "https://yandex.ru/news?from=tabbar".
yandex_news()
# pprint(news)


# ================================ #
# 2. Сложить собранные данные в БД #
# ================================ #


def mongo_insert_unique(documents):
    """
    Добавление нового документа в коллекцию c предварительной проверкой на его наличие в ней
    (проверка дублирования записей).

    Parameters:
    ----------
    documents: dict
        Документ который необходимо добать в коллекцию.

    """
    for news in documents:
        collection.update(news, news, upsert=True)


def mongo_brows(fields_list):
    """
    Просмотр документов в коллекции БД MongoDB.

    Parameters:
    ----------
    fields: 'dict'
        Список полей для отображения.

    """
    if fields == {}:
        result = collection.find(fields)
    else:
        result = collection.find({}, fields)

    for news in result:
        pprint(news)


# ================================================= #
# Работаем с MongoDB. Подключение к БД news_db #
# ================================================= #
db_name = 'news_db'
client = MongoClient('localhost', 27017)
db = client[db_name]
collection = db.news_collection

# fields = {'_id': True, 'name': True, 'link': True, 'date': True, 'source': True}
fields = {}  # Просматриваем все поля

# =================================================================== #
# Очищаем коллекцию (при необходимости, если не надо закоментировать) #
# =================================================================== #
# collection.delete_many({})

# =================================================================== #
# Добавляем записи в базу. Осуществляем проверку дублирования записей #
# =================================================================== #
print('\n---------\n2 задание\n---------')
mongo_insert_unique(news)  # Проверка дублирования записей

# Показываем документы коллекции
mongo_brows(fields)
