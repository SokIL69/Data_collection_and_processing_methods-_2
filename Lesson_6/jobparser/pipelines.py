# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy2003

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        # self.process_item(item['salary'])
        ready_salary = self.process_salary(item['salary'], spider.name)
        item['min_salary'] = ready_salary[0]
        item['max_salary'] = ready_salary[1]
        item['currency'] = ready_salary[2]
        del item['salary']
        collection.insert_one(item)
        return item

    def process_salary(self, salary, name):
        # Возвращаем валюту и значение зарплаты (мин. и мак. значения)
        s_min = None
        s_max = None
        # hh.ru
        if name == 'hhru':
            if salary[0] == 'з/п не указана':
                s_currency = None
            elif salary[0].replace(' ', '') == 'от':  # "от 250\xa0000 руб."
                s_min = salary[1].replace('\xa0', '')
                if salary[4].replace(' ', '') == 'наруки':
                    s_currency = salary[3]
                else:
                    s_currency = salary[5]
                    s_max = salary[3].replace('\xa0', '')
            elif salary[0].replace(' ', '') == 'до':  # 'до 230\xa0000 руб.'
                s_currency = salary[3]
                s_max = salary[1].replace('\xa0', '')
            else:  # "70\xa0000 - 400\xa0000 руб."
                s_currency = salary[3]
                s_min = salary[0].replace('\xa0', '')
                s_max = salary[1].replace('\xa0', '')

        # superjob.ru
        if name == 'sjru':
            if salary[0] == 'По договорённости':
                s_currency = None
            elif salary[0].replace(' ', '') == 'от':  # ['от', '\xa0', '300\xa0000\xa0руб.']
                s_min = salary[2].replace('\xa0', ' ').split(' ')
                s_currency = s_min.pop(len(s_min) - 1)
                s_min = ''.join(s_min)
            elif salary[0].replace(' ', '') == 'до':  # ['до', '\xa0', '30\xa0000\xa0руб.']
                s_max = salary[2].replace('\xa0', ' ').split(' ')
                s_currency = s_max.pop(len(s_max) - 1)
                s_max = ''.join(s_max)
            else:  # ['160\xa0000', '200\xa0000', '\xa0', 'руб.']
                s_currency = salary[3]
                s_min = salary[0].replace('\xa0', '')
                s_max = salary[1].replace('\xa0', '')

        if s_min is not None:
            s_min = float(s_min)
        if s_max is not None:
            s_max = float(s_max)

        salary_list = []
        salary_list.append(s_min)
        salary_list.append(s_max)
        salary_list.append(s_currency)

        return salary_list