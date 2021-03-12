# Методы сбора и обработки данных из сети Интернет
# Соковнин Игорь Леонидович
#
# Урок 2. Парсинг HTML. BeautifulSoup, MongoDB
#
# Задание 1. Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
# с сайтов Superjob и HH. Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
# - Наименование вакансии.
# - Предлагаемую зарплату (отдельно минимальную и максимальную).
# - Ссылку на саму вакансию.
# - Сайт, откуда собрана вакансия.
#
# ### По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas.
#
# 1.1  Сбор информации о вакансиях на вводимую должность сайта Superjob
# https://www.superjob.ru/vacancy/search/?keywords=python
# "superjob структура вакансии.txt" - описание структуры заявки
#

import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import time  # Модуль для работы со значением времени
import json  # Пакет для удобной работы с данными в формате json


def get_superjob_salary(s: str):
    """Возвращаем валюту, период и значение зарплаты (мин. и мак.)"""

    s = s.split('\xa0')
    s_type = 1
    if s[0] == 'По договорённости':
        s_flag = 0  # ['По договорённости']
        s_type = 0
    elif s[0] == 'от':
        s_flag = 1  # ['от', '210', '000', 'руб.']
        s_type = 1
    elif s[0] == 'до':
        s_flag = 2  # ['до', '50', '000', 'руб.']
        s_type = 2
    else:
        s_flag = 3  # ['60', '000', '—', '75', '000', 'руб.']
        s_type = 3

    fl = 0  # '—'
    s_min = ''  # None
    s_max = ''  # None
    s_currency = ''  # None

    if s_flag != 0:
        s_currency = s[len(s) - 1]

    # for i, item in enumerate(s):
    for i in range(len(s)):
        if s_flag == 1:
            if s[i].isdigit():
                s_min = s_min + s[i]  # не принимает None значение
        if s_flag == 2:
            if s[i].isdigit():
                s_max = s_max + s[i]
        if s_flag == 3:
            if s[i] == '—':
                fl = 1
            if fl == 0:
                if s[i].isdigit():
                    s_min = s_min + s[i]
            else:
                if s[i].isdigit():
                    s_max = s_max + s[i]

    if s_min.isdigit():
        s_min = int(s_min)
    else:
        s_min = None
    if s_max.isdigit():
        s_max = int(s_max)
    else:
        s_max = None
    if s_currency == '':
        s_currency = None

    return s_min, s_max, s_currency, s_type


# Основная часть
main_link = 'https://www.superjob.ru/'
page = 1
vacancies = []
print(f"Поиск вакансий на сайте {main_link}:")

keywords = 'Data Scientist'
#keywords = 'python'
#keywords = 'Слонопатам'

while page != None:
    print(f"Страница: {page}")
    params = {
        'keywords': keywords,
        'page': str(page)  #'1'
    }
    search_link = main_link + 'vacancy/search/'
    response = requests.get(search_link, params=params)
    soup = bs(response.text, 'html.parser')

    div_id_app = soup.find(attrs={'id': 'app'})
    elements = div_id_app.findAll('div', recursive=True, attrs={'class': 'f-test-search-result-item'})
    # pprint(elements)
    for child in elements:
        vacancies_data = {}
        flag = False
        # 1. Наименование вакансии + 3. Ссылку на саму вакансию
        children_element = child.find('a', attrs={'class': '_6AfZ9'})
        if children_element:
            flag = True
            vacancies_link = children_element['href']  # & children_element.attrs['href']
            vacancies_text = children_element.getText()  # & children_element.text
            vacancies_data['vacansii_name'] = vacancies_text
            vacancies_data['vacansii_link'] = main_link + vacancies_link
            vacancies_data['www'] = main_link

        children_element = child.find('span', attrs={'class': 'f-test-text-company-item-salary'})
        # 2. Предлагаемая зарплата (отдельно минимальную и максимальную, валюту, период).
        if children_element:
            flag = True
            salaries = children_element.findAll('span', attrs={'class': 'PlM3e'})
            for salary in salaries:
                salary_element = salary.find('span', attrs={'class': 'PlM3e'})
                salary_element = salary.getText()
                if salary_element == "месяц":
                    vacancies_data['salary_period'] = salary_element
                else:
                    vacancies_data['salary_min'], vacancies_data['salary_max'], vacancies_data['currency'], \
                        vacancies_data['s_type'] = get_superjob_salary(salary_element)

            #if flag:
            #    vacancies.append(vacancies_data)

        # 6. Описание вакансии
        children_element = child.find('span', attrs={'class': '_38T7m'})
        if children_element:
            vacancies_text = children_element.getText()  # & children_element.text
            vacancies_data['vacansii_desc'] = vacancies_text

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
                vacancies_data['vacansii_type_work'] = vacancies_text
            else:
                vacancies_data['vacansii_type_work'] = None

        if flag:
            vacancies.append(vacancies_data)

    # переход на следующую страницу
    # <a rel="next" class="icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe" target="_self"
    #    href="/vacancy/search/?keywords=python&amp;page=2">
    page = None
    a_next = soup.find('a', recursive=True, attrs={'class': 'f-test-link-Dalshe'})
    if a_next:
        a_next_link = a_next['href']  # & children_element.attrs['href']
        page_list = a_next_link.split('/vacancy/search/?keywords=python&page=')
        page = page_list[len(page_list) - 1]

    # Необязательная задержка, чтобы не нагружать сервисы.
    time.sleep(0.25)

# отображаем введённую информацию
print(f"Поиск вакансий на сайте {main_link} завершён.")
number_superjob = len(vacancies)
print(f"Найдено {number_superjob} вакансий.")
# pprint(vacancies)

###############################################
# 1.2  Сбор информации о вакансиях на вводимую должность сайта hh
# 'https://hh.ru'
# lesson_2_hw_1_2_1.txt - описание структуры заявки


def get_hh_salary(s: str):
    """Возвращаем валюту, период и значение зарплаты (мин. и мак.)"""

    s = s.replace('\xa0', '')
    s = s.replace('-', ' ')
    #print(s)
    # "70\xa0000 - 400\xa0000 руб."
    # "от 250\xa0000 руб."
    # 'до 230\xa0000 руб.'
    # ''
    s = s.split(' ')
    #print(s)
    s_type = 1
    if s[0] == '':
        s_flag = 0  # ['']
        s_type = 0
    elif s[0] == 'от':
        s_flag = 1  # ['от', '250000', 'руб.']
        s_type = 1
    elif s[0] == 'до':
        s_flag = 2  # ['до', '230000', 'руб.']
        s_type = 2
    else:
        s_flag = 3  # ['70000', '400000', 'руб.']
        s_type = 3

    fl = 0  # '—'
    s_min = ''  # None
    s_max = ''  # None
    s_currency = None

    if s_flag != 0:
        s_currency = s[2]
    if s_flag == 1:
        s_min = s[1]
    if s_flag == 2:
        s_max = s[1]
    if s_flag == 3:
        s_min = s[0]
        s_max = s[1]

    if s_min.isdigit():
        s_min = int(s_min)
    else:
        s_min = None
    if s_max.isdigit():
        s_max = int(s_max)
    else:
        s_max = None

    return s_min, s_max, s_currency, s_type

# https://hh.ru/search/vacancy?area=113&text=python&page=0
main_link = 'https://hh.ru'
#keywords = 'Data Scientist'
#keywords = 'python'
#keywords = 'Слонопатам'
page = 0
#vacancies = []
print(f"\nПоиск вакансий на сайте {main_link}:")
while page != None:
    print(f"Страница: {page}")
    params = {
        'area': '113',
        'text': keywords,
        'page': str(page)
    }

    # С этим headers возвращается status_code = 404 --> Windows NT 6.2
    headers = {'User Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
    # С этим headers возвращается status_code = 200 --> Windows NT 10.0
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36'}

    response = requests.get(main_link + '/search/vacancy', params=params, headers=headers)

    #print(response.status_code)
    if response.ok:
        soup = bs(response.text, 'html.parser')
        div_vacancy_serp = soup.find(attrs={'class': 'vacancy-serp'})  # тег верхнего уровня
        elements = div_vacancy_serp.findAll('div', recursive=True, attrs={'class': 'vacancy-serp-item'})
        for child in elements:
            vacancies_data = {}
            vacancies_name = child.find('a', attrs={'class': 'bloko-link'})
            vacancies_link = vacancies_name['href']
            vacancies_text = vacancies_name.getText()
            vacancies_data['vacansii_name'] = vacancies_text
            vacancies_data['vacansii_link'] = vacancies_link
            vacancies_data['www'] = main_link
            # div_vacancy_serp = soup.find(attrs={'class': 'vacancy-serp-item__info'})
            div_user_content = child.find('div', attrs={'class': 'g-user-content'})
            #vacancies_data['vacansii_desc'] = div_user_content.find('div',
            #        attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).getText()
            vacancies_data['vacansii_desc'] = div_user_content.find('div').getText()
            employer = child.find('a', attrs={'class': 'bloko-link_secondary'})
            if employer:
                vacancies_data['employer'] = employer.getText()
            vacancies_data['vacansii_type_work'] = None
            # salary
            span_salary = child.find('div', attrs={'vacancy-serp-item__sidebar'})
            if span_salary:
                if span_salary.find('span'):
                    salary_element = span_salary.find('span').getText()
                    #vacancies_data['salary'] = salary_element
                    vacancies_data['salary_min'], vacancies_data['salary_max'], vacancies_data['currency'], \
                                vacancies_data['s_type'] = get_hh_salary(salary_element)
                else:
                    vacancies_data['salary_min'] = None
                    vacancies_data['salary_max'] = None
                    vacancies_data['currency'] = None
                    vacancies_data['s_type'] = 0

            vacancies.append(vacancies_data)

    # переход на следующую страницу
    # <a rel="next" class="icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe" target="_self"
    #    href="/vacancy/search/?keywords=python&amp;page=2">
    page = None
    a_next = soup.find('a', recursive=True, attrs={'class': 'HH-Pager-Controls-Next'})
    if a_next:
        a_next_link = a_next['href']  # & children_element.attrs['href']
        page_list = a_next_link.split('/search/vacancy?L_is_autosearch=false&amp;area=113&amp;clusters=true&amp;enable_snippets=true&amp;text=python&amp;page=')
        page_list = a_next_link.split('page=')
        page = page_list[len(page_list) - 1]

    # Необязательная задержка, но чтобы не нагружать сервисы hh, оставим. 5 сек мы может подождать
    time.sleep(0.25)

print(f"Поиск вакансий на сайте {main_link} завершён.")
number_hh = len(vacancies)
print(f"На сайте {main_link} найдено {number_hh - number_superjob} вакансий.")

###############################################

# отображаем введённую информацию
print(f"\nУсловие поиска: {params['text']}")
print(f"Найденные вакансии.")
pprint(vacancies)

# Создаем файл в формате json, записываем в него результат и закрываем файл
with open('lesson_2_hw_1.json', 'w', encoding='utf-8') as file:
    json.dump(vacancies, file, indent=2, ensure_ascii=False)