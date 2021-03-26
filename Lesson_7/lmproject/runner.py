# Самописная "кнопка" запуска паука
from scrapy.crawler import CrawlerProcess   # Головной класс для работы паука
from scrapy.settings import Settings # Настройки глобальные настройки

# Подключение локальных настроек (файл settings.py)
from lmproject import settings
from lmproject.spiders.lmru import LmruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)  # чтение наших настроек

    process = CrawlerProcess(settings=crawler_settings)
    search_list = ['фанера', 'ковер']
    # search_list = ['фанера']
    # input('')
    for item in search_list:
        process.crawl(LmruSpider, query=item)
    # process.crawl(LmruSpider, query='фанера')
    # process.crawl(LmruSpider, query='ковер')

    process.start()

#
# Работаем с MongoDB
#
from pymongo import MongoClient
from pprint import pprint


def mongo_brows(fields_list):
    # Просмотр документов в коллекции БД MongoDB.
    if fields == {}:
        result = collection.find(fields)
    else:
        result = collection.find({}, fields)

    for news in result:
        pprint(news)


# ================================================ #
# Работаем с MongoDB. Подключение к БД leroymerlin #
# ================================================ #
db_name = 'leroymerlin'
client = MongoClient('localhost', 27017)
db = client[db_name]
collection = db.lmru

# fields = {'_id': True, 'name': True, 'link': True, 'date': True, 'source': True}
fields = {}  # Просматриваем все поля

# Показываем документы коллекции
mongo_brows(fields)

# {'_id': ObjectId('605e13018e701018fe285428'),
#  'def_list': {'Вес товара в индивидуальной упаковке (кг)': '5.56',
#               'Вес, кг': '5.56',
#               'Влагостойкий': 'Да',
#               'Высота товара в индивидуальной упаковке (см)': '1.2',
#               'Глубина товара в индивидуальной упаковке (см)': '122.0',
#               'Длина (см)': '122.0',
#               'Допустимое отклонение толщины (мм)': '0.5',
#               'Допустимое отклонения длины (мм)': '2.0',
#               'Классэмиссии формальдегида': 'E1',
#               'Модуль упругости (МПа)': '4500.0',
#               'Назначение': 'Кровля, Мебель, Пол, Полы по лагам, Потолок, '
#                             'Различная отделка, Стена',
#               'Основной материал': 'Фанера',
#               'Плотность (кг/м³)': '660.0',
#               'Площадь (м²)': '0.7',
#               'Покрытие': 'Шлифованный',
#               'Полезная площадь (м²)': '0.73',
#               'Порода древесины': 'Лиственница',
#               'Предел прочности при изгибе, второстепенная ось (Мпа), не менее': '45.0',
#               'Предел прочности при изгибе, главная ось (Мпа), не менее': '60.0',
#               'Размер (Д х Ш х В) (мм)': '600х1220х12',
#               'Содержит древесину': 'Да',
#               'Сорт': '1/3',
#               'Страна производства': 'Россия',
#               'Страна происхождения древесины': 'Россия',
#               'Тип продукта (локальный)': 'Фанера',
#               'Тип соединения деревянных деталей': 'С зазором',
#               'Тип упаковки': 'Без упаковки',
#               'Толщина (мм)': '12.0',
#               'Форма': 'Прямоугольный',
#               'Цвет': 'Бежевый',
#               'Ширина (см)': '60.0',
#               'Ширина товара в индивидуальной упаковке (см)': '60.0'},
#  'name': ['Фанера 12 мм лиственница 600Х1220 мм сорт 1/3 0.732 м²'],
#  'photos': [{'checksum': 'c8fc2bd3372d893cc1158fc4b5b058d7',
#              'path': 'Фанера 12 мм лиственница 600Х1220 мм сорт 1/3 0.732 '
#                      'м²/63a72aa3fdb6a047f5550093a4fd20ba447ee93f.jpg',
#              'status': 'downloaded',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82091667.jpg'},
#             {'checksum': 'b6ab11ee48c2d18c094f711ab3de9238',
#              'path': 'Фанера 12 мм лиственница 600Х1220 мм сорт 1/3 0.732 '
#                      'м²/3300561a9725635cd7b52e6e1360b1757bd3ed2b.jpg',
#              'status': 'downloaded',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82091667_01.jpg'},
#             {'checksum': '1186b5c2d1e8fe05dc66a63a7d764fed',
#              'path': 'Фанера 12 мм лиственница 600Х1220 мм сорт 1/3 0.732 '
#                      'м²/fdf86254bd93c21eafb79a046cb4ecd23c87c15c.jpg',
#              'status': 'downloaded',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82091667_02.jpg'}],
#  'url': ['https://perm.leroymerlin.ru/product/fanera-12-mm-listvennica-600h1220-mm-sort-1-3-0-732-m-82091667/']}
