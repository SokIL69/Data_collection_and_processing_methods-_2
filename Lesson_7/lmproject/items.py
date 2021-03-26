# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def process_url(value):
    if value:
        value = value.replace('w_82,h_82', 'w_2000,h_2000')
    return value


def process_def_list(value):
    if value:
        value = value.replace('  ', '').replace('\n', '')
        # tth = value.xpath('//dt[@class="def-list__term"]/text()')
        # tth_value = value.xpath('//dd[@class="def-list__definition"]/text()')
        # value = dict(tth=tth_value)
    return value


# class LmProjectPipeline(scrapy.Item):
class LmParserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()  # Наименование товара
    # photos = scrapy.Field()  # Описание файлов изображений

    # Ускорение работы паука на 30%
    # Здесь делаем мелкую очистку данных
    name = scrapy.Field(outpun_processor=TakeFirst())  # используем постобработчик
    photos = scrapy.Field(input_processor=MapCompose(process_url))  # Функция process_url будет применена
                                                                    # к каждому элементу списка внутри photos
    #def_list = scrapy.Field()

    def_list = scrapy.Field(input_processor=MapCompose(process_def_list))  # Характеристики товара
    url = scrapy.Field()  # Источник данных
    _id = scrapy.Field()


# {'_id': ObjectId('605db83e64e651122a863d0a'),
#  'def_list': ['Назначение',
#               'Жилое помещение',
#               'Ширина (см)',
#               '250.0',
#               'Длина (см)',
#               '350.0',
#               'Высота ворса (мм)',
#               '12.0',
#               'Размер (ДxШ) (в см)',
#               '250x350',
#               'Количество точек на м²',
#               '480000',
#               'Общая толщина (мм)',
#               '14.0',
#               'Плотность (г/м²)',
#               '1623',
#               'Общий вес (г/м²)',
#               '2559.0',
#               'Форма ковра',
#               'Прямоугольный',
#               'Цвет',
#               'Серый',
#               'Цветовая палитра',
#               'Серый / Серебристый',
#               'Стиль',
#               'Дизайнерский',
#               'Страна производства',
#               'Россия',
#               'Состав (%)',
#               '100% Полипропилен',
#               'Материал основы',
#               'Джут',
#               'Основной материал',
#               'Полипропилен',
#               'Противоскользящее покрытие',
#               'Нет',
#               'Марка',
#               'MERINOS',
#               'Уход',
#               'Пылесос',
#               'Тип упаковки',
#               'Термоусадочная упаковка',
#               'Вес, кг',
#               '21.24',
#               'Тип продукта',
#               'Ковер'],
#  'name': ['Ковёр Mega Carving D264 2.5x3.5 м полипропилен'],
#  'photos': [{'checksum': '2532854e1f6cc5f794467f7402e4646a',
#              'path': 'full/684d7ab1d94949353832aab29dc73c7e1803578b.jpg',
#              'status': 'uptodate',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/17923881.jpg'},
#             {'checksum': '4c09f3f428a253485efa305851b4677e',
#              'path': 'full/63817681c3f73f2a1f2879ed8a2028d3d9b1fa07.jpg',
#              'status': 'uptodate',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/17923881_01.jpg'},
#             {'checksum': 'eb4f39e8066dcf5e9b76c4080454a4d2',
#              'path': 'full/8241bd2c3d91bb869986c2346ab614aa022fb92e.jpg',
#              'status': 'uptodate',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/17923881_02.jpg'},
#             {'checksum': 'e600023882d4bcb188ebfd6cf988e5cc',
#              'path': 'full/ae598b34ea566614db6c982a88e662684a2e9947.jpg',
#              'status': 'uptodate',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/17923881_03.jpg'}],
#  'url': ['https://perm.leroymerlin.ru/product/kover-mega-carving-d264-2-5x3-5-m-polipropilen-17923881/']}