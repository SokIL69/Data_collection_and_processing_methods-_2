# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline  # для работы с файлами
from pymongo import MongoClient
import scrapy
import hashlib
from scrapy.utils.python import to_bytes

file_dir = ''  # Имя дирректории для файлов


def list_to_dict(def_list):
    # Окончательно формируем поле def_list - характеристики товара
    def_list_new = {}
    for i in range(len(def_list) // 2):
        i *= 2
        def_list_new[def_list[i]] = def_list[i + 1]
    return def_list_new


class LmProjectPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin

    def process_item(self, item, spider):
        # Добавить работу с БД
        collection = self.mongo_base[spider.name]
        item['def_list'] = list_to_dict(item['def_list'])
        collection.insert_one(item)
        return item


class LmPhotosPipeLine(ImagesPipeline):
    # Создаём pipeline для работы с файлами
    def get_media_requests(self, item, info):
        # Объект spider.info содержит данные о процессе загрузки
        if item['photos']:
            for img in item['photos']:  # пытаемся скачать файл
                try:
                    # меняем ссылку для получения картинок хорошего качества
                    # yield scrapy.Request(img.replace('w_82,h_82', 'w_2000,h_2000'))
                    # перенесли в itemloaders (см. items.py)
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    # Создаём дирректории для файлов с осмысленными именами
    # Для файлов высокого разрешения
    def file_path(self, request, response=None, info=None, *, item=None):
        global file_dir
        file_dir = item["name"][0]
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        # return f'full/{image_guid}.jpg'
        return f'{file_dir}/{image_guid}.jpg'

    # Для файлов низкого разрешения
    def thumb_path(self, request, thumb_id, response=None, info=None):
        thumb_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        # return f'thumbs/{thumb_id}/{thumb_guid}.jpg'
        return f'thumbs/{thumb_id}/{file_dir}/{thumb_guid}.jpg'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]  # Генератор списка
        # В методе класса который будет работать последним, нужно всегда возвращать item
        return item


# Картинка низкого качества
# https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_82,h_82,c_pad,b_white, d_photoiscoming.png/LMCode/82380587.jpg
# Картинка высокого качества
# https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82380587.jpg

# item:
# {'name': 'Ковёр «Фиеста» 80610-55, 1.6х2.3 м',
#  'photos': ['https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_82,h_82,c_pad,b_white,d_photoiscoming.png/LMCode/82152277.jpg',
#             'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_82,h_82,c_pad,b_white,d_photoiscoming.png/LMCode/82152277_02.jpg',
#             'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_82,h_82,c_pad,b_white,d_photoiscoming.png/LMCode/82152277_03.jpg',
#             'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_82,h_82,c_pad,b_white,d_photoiscoming.png/LMCode/82152277_04.jpg']}

# results:
# [(True,  # Если False - файл не скачался, есть проблема
#   {'checksum': '4916416ced8de29195dbe3ac7539f482',  # crc-файла
#    'path': 'full/c8188dd44095e05bc8a38803cab6b17b08a8cc79.jpg',  # Имя под которым сохранился файл
#    'status': 'downloaded',  # если uptodate - в дирректории уже есть файл с такой crc (повторно не закачивается)
#    'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82152277.jpg'}), ]

# item:
# {'name': 'Ковёр «Гарда Модерн», 0.6х1 м, цвет бежевый',
#  'photos': [{'checksum': '3bc035fb54d8689ca876a9e2e5b6e622',
#              'path': 'full/bce3adc9a5b2cb10afa1c966fdf6e19b9f9eb4c0.jpg',
#              'status': 'downloaded',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82172625.jpg'},
#             {'checksum': '2c7e365aa9112cc2c12436e9f339d546',
#              'path': 'full/dd680170b51684bbb3c55f9c4b9e6196cc4fa7dc.jpg',
#              'status': 'downloaded',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82172625_01.jpg'},
#             {'checksum': '617338414fa89ff975a8e949f8f504ea',
#              'path': 'full/2cd774ba161e62dd7e0285b7952fb10f702695db.jpg',
#              'status': 'downloaded',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82172625_02.jpg'},
#             {'checksum': '4d62e3fb5f8eb7edb18e649587ca10ee',
#              'path': 'full/8304f84351d9ee7d1f5d5a852c6e11bb924bb033.jpg',
#              'status': 'downloaded',
#              'url': 'https://res.cloudinary.com/lmru/image/upload/f_auto,q_90,w_2000,h_2000,c_pad,b_white,d_photoiscoming.png/LMCode/82172625_03.jpg'}]}

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
