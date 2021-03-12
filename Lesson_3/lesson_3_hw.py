# Методы сбора и обработки данных из сети Интернет
# Соковнин Игорь Леонидович
#
# Урок 3. Системы управления базами данных MongoDB и SQLite в Python
#
# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
#    записывающую собранные вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.


import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import time  # Модуль для работы со значением времени
import json  # Пакет для удобной работы с данными в формате json
from pymongo import MongoClient
from bson.objectid import ObjectId


#
# Урок 3. Системы управления базами данных MongoDB и SQLite в Python
# Основная часть: строка 343 !


# Задание 1.
# Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
# и реализовать функцию, записывающую собранные вакансии в созданную БД.
def mongo_insert(ins_type: 0, dictionary):
    """
    Добавление новой записи в MongoDB (без проверки дублирования записей).

    Parameters:
    ----------
    insert_type: int, default = 0
        0 - добавлеем все документы сразу, без проверки, 1 -  добавлем каждый документ по отдельности.

    dictionary: dict
        Список документов.

    """
    if insert_type == 0:
        collection.insert_many(dictionary)

    if insert_type == 1:
        for vacancy in dictionary:
            collection.insert_one(vacancy)


# Задание 2.
# Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
def mongo_salary_find(salary_value: 0):
    """
    Производим поиск и вывод на экран вакансии с заработной платой больше введённой суммы.

    Parameters:
    ----------
    salary: float, default = 0
        Размер заработной платы для поиска.

    """
    result = collection.find({'$or': [{'salary_min': {'$gte': salary_value}}, {'salary_max': {'$gte':  salary_value}}]})

    for vacancy_1 in result:
        pprint(vacancy_1)


# Задание 3.
# Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
def mongo_insert_unique(documents):
    """
    Добавление нового документа в коллекцию c предварительной проверкой на его наличие в ней
    (проверка дублирования записей).

    Parameters:
    ----------
    documents: dict
        Документ который необходимо добать в коллекцию.

    """
    # result = documents.find({})
    for vacancy in documents:
        collection.update(vacancy, vacancy, upsert=True)

    """
    find_doc = False
    result = collection.find({})
    for vacancy in result:
        if (vacancy == document):
            find_doc = True
            break

    if find_doc == False:
        collection.insert_one(document)
    """


# def mongo_brows(collection_name, fields):
def mongo_brows(fields_list):
    """
    Просмотр документов в коллекции БД MongoDB.

    Parameters:
    ----------
    fields: 'dict'
        Список полей для отображения.

    """
    if fields == {}:
        result = collection.find(fields)
    else:
        result = collection.find({}, fields)

    for vacancy_1 in result:
        pprint(vacancy_1)


# ============================== #
# ============================== #
# ============================== #
def get_superjob_salary(s: str):
    """
    Возвращаем валюту и значение зарплаты (мин. и мак.)

    """
    s = s.split('\xa0')
    if s[0] == 'По договорённости':
        s_min = None
        s_max = None
        s_currency = None
    elif s[0] == 'от':  # ['от', '210', '000', 'руб.']
         s.pop(0)
         s_currency = s.pop(len(s) - 1)
         # s_min = s[0: len(s)].pop()
         s_min = ''.join(s)  # s[0: len(s)].pop()
         s_max = None
    elif s[0] == 'до':  # ['до', '50', '000', 'руб.']
        s.pop(0)
        s_currency = s.pop(len(s) - 1)
        s_min = None
        # s_max = s[0: len(s)].pop()
        s_max = ''.join(s)
    elif '—' in s:  # ['60', '000', '—', '75', '000', 'руб.']
        s_currency = s.pop(len(s) - 1)
        s = ''.join(s).split('—')
        s_min = s.pop(0)
        s_max = s.pop(0)
    else:  # ['60', '000', 'руб.']
        s_currency = s.pop(len(s) - 1)
        s = ''.join(s).split('—')
        s_min = s.pop(0)
        s_max = s_min

    if s_min is not None:
        s_min = float(s_min)
    if s_max is not None:
        s_max = float(s_max)

    return s_min, s_max, s_currency


def parse_superjob(text):
    """
     Поиск вакансий на сайте https://www.superjob.ru/

    """
    main_link = 'https://www.superjob.ru/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/89.0.4389.72 Safari/537.36',
               'Accept': '*/*'}
    page = 1
    # vacancies = []
    print(f"Поиск вакансий на сайте {main_link}:")
    while page is not None:
        print(f"Страница: {page}")
        params = {
            'keywords': text,
            'page': str(page)  #'1'
        }
        search_link = main_link + 'vacancy/search/'
        response = requests.get(search_link, params=params, headers=headers)
        soup = bs(response.text, 'html.parser')

        div_id_app = soup.find(attrs={'id': 'app'})
        elements = div_id_app.findAll('div', recursive=True, attrs={'class': 'f-test-search-result-item'})
        for child in elements:
            vacancies_data = {}
            success = False # исключаем добавление пустых записей
            # 1. Наименование вакансии + 3. Ссылку на саму вакансию
            children_element = child.find('a', attrs={'class': '_6AfZ9'})
            if children_element:
                success = True
                vacancies_link = children_element['href']
                vacancies_text = children_element.getText()
                vacancies_data['vacancy_name'] = vacancies_text
                vacancies_data['vacancy_link'] = main_link + vacancies_link
                vacancies_data['www'] = main_link

            # 2. Предлагаемая зарплата (отдельно минимальную и максимальную, валюту, период).
            children_element = child.find('span', attrs={'class': 'f-test-text-company-item-salary'})
            if children_element:
                salaries = children_element.findAll('span', attrs={'class': 'PlM3e'})
                for salary in salaries:
                    salary_element = salary.getText()
                    vacancies_data['salary_period'] = None
                    if salary_element == "месяц":
                        vacancies_data['salary_period'] = salary_element
                    else:
                        vacancies_data['salary_min'], vacancies_data['salary_max'], vacancies_data['currency'] = \
                            get_superjob_salary(salary_element)

            # 6. Описание вакансии
            children_element = child.find('span', attrs={'class': '_38T7m'})
            if children_element:
                vacancies_text = children_element.getText()  # & children_element.text
                vacancies_data['vacancy_desc'] = vacancies_text

            # 7. Работодатель
            children_element = child.find('span', attrs={'class': '_9fXTd'})
            if children_element:
                vacancies_text = children_element.getText()  # & children_element.text
                vacancies_data['employer'] = vacancies_text

            # 8. Удалённая работа
            children_element = child.find('div', attrs={'class': '_9_FPy'})
            if children_element:
                vacancies_text = children_element.getText()  # & children_element.text
                if vacancies_text == "Удаленная работа":
                    vacancies_data['vacancy_type_work'] = vacancies_text
                else:
                    vacancies_data['vacancy_type_work'] = None

            if success:
                vacancies.append(vacancies_data)

        # переход на следующую страницу
        if soup.find('a', recursive=True, attrs={'class': 'HH-Pager-Controls-Next'}) is not None:
            page += 1
        else:
            page = None

        # Необязательная задержка, чтобы не нагружать сервисы.
        time.sleep(0.25)

    # Отображаем введённую информацию
    print(f"Поиск вакансий на сайте {main_link} завершён.")
    number_superjob = len(vacancies)
    print(f"Найдено {number_superjob} вакансий.")


def get_hh_salary(s: str):
    """
    Возвращаем валюту и значение зарплаты (мин. и мак.)

    """
    s = s.replace('\xa0', '').replace('-', ' ').split(' ')
    s_min = None
    s_max = None
    if s[0] == '':
        s_currency = None
    elif s[0] == 'от':  # "от 250\xa0000 руб."
        s_currency = s[2]
        s_min = s[1]
    elif s[0] == 'до':  # 'до 230\xa0000 руб.'
        s_currency = s[2]
        s_max = s[1]
    else:   # "70\xa0000 - 400\xa0000 руб."
        s_currency = s[2]
        s_min = s[0]
        s_max = s[1]

    if s_min is not None:
        s_min = float(s_min)
    if s_max is not None:
        s_max = float(s_max)

    return s_min, s_max, s_currency


def parse_hh(text):
    """
    Поиск вакансий на сайте https://hh.ru/

    """
    main_link = 'https://hh.ru'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/89.0.4389.72 Safari/537.36',
               'Accept': '*/*'}
    page = 0
    print(f"\nПоиск вакансий на сайте {main_link}:")
    while page is not None:
        print(f"Страница: {page}")
        params = {
            'area': '113',
            'text': text,
            'page': str(page)
        }
        response = requests.get(main_link + '/search/vacancy', params=params, headers=headers)
        if response.ok:
            soup = bs(response.text, 'html.parser')
            div_vacancy_serp = soup.find(attrs={'class': 'vacancy-serp'})  # тег верхнего уровня
            elements = div_vacancy_serp.findAll('div', recursive=True, attrs={'class': 'vacancy-serp-item'})
            for child in elements:
                vacancies_data = {}
                vacancies_name = child.find('a', attrs={'class': 'bloko-link'})
                vacancies_link = vacancies_name['href']
                vacancies_text = vacancies_name.getText()
                vacancies_data['vacancy_name'] = vacancies_text
                vacancies_data['vacancy_link'] = vacancies_link
                vacancies_data['www'] = main_link
                div_user_content = child.find('div', attrs={'class': 'g-user-content'})
                vacancies_data['vacancy_desc'] = div_user_content.find('div').getText()
                employer = child.find('a', attrs={'class': 'bloko-link_secondary'})
                if employer:
                    vacancies_data['employer'] = employer.getText()
                vacancies_data['vacancy_type_work'] = None
                # salary
                span_salary = child.find('div', attrs={'vacancy-serp-item__sidebar'})
                if span_salary:
                    if span_salary.find('span'):
                        salary_element = span_salary.find('span').getText()
                        vacancies_data['salary_min'], vacancies_data['salary_max'], vacancies_data['currency'] = \
                            get_hh_salary(salary_element)
                    else:
                        vacancies_data['salary_min'] = None
                        vacancies_data['salary_max'] = None
                        vacancies_data['currency'] = None

                vacancies.append(vacancies_data)

        # переход на следующую страницу
        if soup.find('a', recursive=True, attrs={'class': 'HH-Pager-Controls-Next'}) is not None:
            page += 1
        else:
            page = None

        # Необязательная задержка, чтобы не нагружать сервисы hh, 5 сек
        time.sleep(0.25)

    print(f"Поиск вакансий на сайте {main_link} завершён.")
    number_hh = len(vacancies)
    # print(f"На сайте {main_link} найдено {number_hh - number_superjob} вакансий.")


# ======================================================================== #
# == Урок 3. Системы управления базами данных MongoDB и SQLite в Python == #
# ======================================================================== #

# ============== #
# Поиск вакансий #
# ============== #

vacancies = []  # Контейнер для вакансий найденных на сайте

# Строка поиска
keywords = 'python'
# keywords = 'Data Scientist'  # Для задания 3.

# Поиск вакансий на сайте https://www.superjob.ru/:
parse_superjob(keywords)

# Поиск вакансий на сайте https://hh.ru:
# При необходимости раскоментарить
# parse_hh(keywords)


# ================================================= #
# Работаем с MongoDB. Подключение к БД vacancies_db #
# ================================================= #
db_name = 'vacancies_db'
client = MongoClient('localhost', 27017)
db = client[db_name]
collection = db.vacancies_collection


# ================================= #
# Задаём список полей для просмотра #
# ================================= #
# fields = {'_id': True, 'vacancy_name': True, 'employer': True}
fields = {}  # Просматриваем все поля


# =================================================================== #
# Очищаем коллекцию (при необходимости, если не надо закоментировать) #
# =================================================================== #
collection.delete_many({})


# =================================================================== #
# Задание 1.  Развернуть у себя
# на компьютере/виртуальной машине/хостинге MongoDB
# и реализовать функцию,
# записывающую собранные вакансии в созданную БД.
# =================================================================== #

# Загружаем документы в коллекцию (без проверки на дубли)
# Просто демонстрация работы
insert_type = 0  # Все документы сразу, без проверки
insert_type = 1  # Каждый документ по отдельности
print('\n--\n1 задание.\n--')
#
# Закоментировать после первого прохода для демонстрации задания 3
#
mongo_insert(insert_type, vacancies)  # без проверки на дубли

# Показываем документы коллекции
mongo_brows(fields)
print('\n\n\n')


# =================================================================== #
# 2 задание. Написать функцию, которая производит поиск и выводит
# на экран вакансии с заработной платой больше введённой суммы.
# =================================================================== #
print('\n--\n2 задание.\n--')
salary = 100000.0
mongo_salary_find(salary)
print('\n\n\n')


# =================================================================== #
# Задание 3. Написать функцию, которая будет добавлять
# в вашу базу данных только новые вакансии с сайта.
# (Проверка дублирования записей).
# =================================================================== #
print('\n--\n3 задание.\n--')
mongo_insert_unique(vacancies)  # Проверка дублирования записей

# Показываем документы коллекции
mongo_brows(fields)


# =================================================================== #
# =================================================================== #
# =================================================================== #


"""
vacancy_1 = [{'currency': 'руб.',
              'employer': 'Компания стартап, резидент Сколково',
              'salary_max': None,
              'salary_min': 300000.0,
              'salary_period': 'месяц',
              'vacancy_desc': 'Создание, согласование и документирование архитектуры '
                              'решения. По функциональным требованиям составлять эпики, '
                              'декомпозировать…Экспертный уровень Python, присылайте '
                              'примеры кода в Github. Опыт управления командной разработки '
                              'от 1 года, проведение код…',
              'vacancy_link': 'https://www.superjob.ru//vakansii/python-team-lead-36050681.html',
              'vacancy_name': 'Python Team lead',
              'vacancy_type_work': 'Удаленная работа',
              'www': 'https://www.superjob.ru/'}
]

vacancy_2 = [{'currency': 'руб.',
              'employer': 'Компания стартап, резидент Сколково',
              'salary_max': 10000.0,
              'salary_min': 30000.0,
              'salary_period': 'месяц',
              'vacancy_desc': 'Создание, согласование и документирование архитектуры '
                              'решения. По функциональным требованиям составлять эпики, '
                              'декомпозировать…Экспертный уровень Python, присылайте '
                              'примеры кода в Github. Опыт управления командной разработки '
                              'от 1 года, проведение код…',
              'vacancy_link': 'https://www.superjob.ru//vakansii/python-team-lead-36050681.html',
              'vacancy_name': 'Python Team lead',
              'vacancy_type_work': 'Удаленная работа',
              'www': 'https://www.superjob.ru/'}
]
"""

# mongo_insert_unique(vacancy_2)
# mongo_insert_unique(vacancy_1)
# Показываем документы коллекции
# mongo_brows(fields)


# ======================================================================== #
# == Урок 3. Системы управления базами данных MongoDB и SQLite в Python == #
# ==                                  END                               == #
# ======================================================================== #


# Отображаем полученную информацию
# print(f"\nУсловие поиска: {keywords}")
# print(f"Найденные вакансии.")
# pprint(vacancies)

# Создаем файл в формате json, записываем в него результат и закрываем файл
# with open('lesson_2_hw_1.json', 'w', encoding='utf-8') as file:
#    json.dump(vacancies, file, indent=2, ensure_ascii=False)

"""
#
# Создаём pandas dataFrame
#
pd.set_option('display.max_rows', 2000)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1000)

df = pd.json_normalize(vacancies)
print(df)

# Выгружаем dataframe в файл
df.to_csv('vacancies.csv', index=False, encoding='utf-8', sep=',')
"""