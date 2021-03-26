import scrapy
from scrapy.http import HtmlResponse
from lmproject.items import LmParserItem
from scrapy.loader import ItemLoader  # Ускорение работы паука на 30%


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://perm.leroymerlin.ru/search/?q=%D0%BA%D0%BE%D0%B2%D0%B5%D1%80']

    # Переопределяем конструктор суперкласса Spider
    def __init__(self, query):
        # Вызываем суперкласс
        super(LmruSpider, self).__init__()
        self.start_urls = [f'https://perm.leroymerlin.ru/search/?q={query}']

    def parse(self, response:HtmlResponse):
        main_link = 'https://perm.leroymerlin.ru/product/'
        # links = response.xpath('//a[@data-qa="product-name"]/@href').extract()
        # Новый подход к сбору ссылок, избавляемся от extract, передаём всю обработку в response

        goods_links = response.xpath('//a[@data-qa="product-name"]')

        for link in goods_links:
            yield response.follow(link, callback=self.parse_good)
        next_page = response.css("a.s15wh9uj_plp::attr('href')").extract_first()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_good(self, response:HtmlResponse):
        # Ускорение работы паука на 30%
        loader = ItemLoader(item=LmParserItem(), response=response)
        # loader.add_xpath('name', '//h1/text()')  # xpath - Возвращает список
        loader.add_css('name', 'h1::text')  # xpath - Возвращает список
        loader.add_xpath('photos', '//img[contains(@slot, "thumbs")]/@src')
        loader.add_value('url', response.url)
        # loader.add_xpath('def_list', '//div[@class="def-list__group"]')
        # Объединяем два xpath в одном запросе
        loader.add_xpath('def_list', '//dt[@class="def-list__term"]/text()' + '|' + '//dd[@class="def-list__definition"]/text()')
        yield loader.load_item()

        # До ускорения
        # name = response.xpath('//h1/text()').extract_first()
        # photos = response.xpath('//img[contains(@slot, "thumbs")]/@src').extract()
        # yield LmProjectPipeline(name=name, photos=photos)


#//div[@class="def-list__group"]
#//dt[@class="def-list__term"]
#//dd[@class="def-list__definition"]

# <div class ="def-list__group" xpath="1">
# <dt class ="def-list__term"> Тип продукта (локальный) </dt>
# <dd class ="def-list__definition">Фанера</dd>
# </div>