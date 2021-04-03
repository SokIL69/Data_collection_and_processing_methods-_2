# -*- coding: utf-8 -*-
# Самописная "кнопка" запуска нашего паука
from scrapy.crawler import CrawlerProcess   # Головной класс для работы паука
from scrapy.settings import Settings # Настройки глобальные настройки

# Подключение локальных настроек (файл settings.py)
from instaparser import settings
from instaparser.spiders.instagram import InstagramSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)  # чтение настроек

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider)

    process.start()


# instagram может забанить на час с ошибкой 429