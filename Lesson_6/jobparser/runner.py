# Самописная "кнопка" запуска нашего паука
from scrapy.crawler import CrawlerProcess   # Головной класс для работы паука
from scrapy.settings import Settings # Настройки глобальные настройки

# Подключение локальных настроек (файл settings.py)
from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.sjru import SjruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)  # чтение наших настроек

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SjruSpider)

    process.start()

