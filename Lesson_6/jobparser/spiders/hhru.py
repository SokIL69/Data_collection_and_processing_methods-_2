import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://perm.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=python&L_save_area=true&area=72&from=cluster_area&showClusters=true']

    def parse(self, response:HtmlResponse):
        links = response.xpath("//a[@data-qa = 'vacancy-serp__vacancy-title']/@href").extract()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)  # функция генератор
        next_page = response.css("a.HH-Pager-Controls-Next::attr('href')").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response:HtmlResponse):
        vacancy_name = response.xpath("//h1//text()").extract()
        vacancy_salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()
        vacancy_source = self.allowed_domains
        yield JobparserItem(name=vacancy_name[0], salary=vacancy_salary, link=response.url, source=vacancy_source[0])
