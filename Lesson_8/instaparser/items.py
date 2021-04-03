# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()  # id пользователя которому принадлежит публикация
    id = scrapy.Field()  # количество лайков за публикацию
    user_name = scrapy.Field()  # имя
    full_name = scrapy.Field()  # расширенное имя
    photo = scrapy.Field()  # ссылка на картинку к публикаии
    post_data = scrapy.Field()  # вся информация о публикации
    parse_user = scrapy.Field()  # вся информация о публикации
    target = scrapy.Field()  # вся информация о публикации
