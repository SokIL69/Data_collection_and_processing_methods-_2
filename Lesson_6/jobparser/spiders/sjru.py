import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']  # allowed_domains = ['sj.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=Automation%20QA%20Engineer%20%2F%20%D0%A2%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA%20%28Python%29',
                  'https://russia.superjob.ru/vacancy/search/?keywords=Head%20of%20Data%20Science',
                  'https://russia.superjob.ru/vacancy/search/?keywords=%D0%93%D0%BB%D0%B0%D0%B2%D0%BD%D1%8B%D0%B9%20%D1%81%D0%BF%D0%B5%D1%86%D0%B8%D0%B0%D0%BB%D0%B8%D1%81%D1%82%20%D0%BE%D1%82%D0%B4%D0%B5%D0%BB%D0%B0%20%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%20%D0%BC%D0%BE%D0%BD%D0%B8%D1%82%D0%BE%D1%80%D0%B8%D0%BD%D0%B3%D0%B0%20%D0%B8%20%D0%BD%D0%B0%D0%B1%D0%BB%D1%8E%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F']
    # start_urls = [
    #     # 'https://www.superjob.ru/vacancy/search/?keywords=Python'
    # ]

    def parse(self, response:HtmlResponse):
        links = response.xpath("//a[contains(@class,'icMQ_ _6AfZ9')]/@href").extract()
        main_link = 'https://www.superjob.ru'
        for link in links:
            page_link = main_link + link
            yield response.follow(page_link, callback=self.vacancy_parse)  # функция генератор
        next_page = response.css("a.f-test-link-Dalshe::attr('href')").extract_first()
        if next_page:
            yield response.follow(main_link + next_page, callback=self.parse)

    def vacancy_parse(self, response:HtmlResponse):
        vacancy_name = response.xpath("//h1/text()").extract()
        vacancy_salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        vacancy_source = self.allowed_domains
        yield JobparserItem(name=vacancy_name[0], salary=vacancy_salary, link=response.url, source=vacancy_source[0])
