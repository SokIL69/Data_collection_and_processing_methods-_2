# Методы сбора и обработки данных из сети Интернет
# Соковнин Игорь Леонидович
#
# Урок 5. Selenium в Python
#
# 1. Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных:
#   - от кого,
#   - дата отправки,
#   - тема письма,
#  - текст письма полный
#
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172
#
# 2. Написать программу, которая собирает «Хиты продаж» с сайта техники mvideo и складывает данные в БД.
# Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары.

import time
# import requests
# from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint
from pymongo import MongoClient


chrom_options = Options()
# Раскрываем окно браузера на максимум
# chrom_options.add_argument('start-maximized')
# driver = webdriver.Chrome(options=chrom_options)

# Вводим задержку иначе страницы не успевают прогрузиться. Величина определяется экспериментально.
delay = 3

# ========================================================================== #
# 1. Написать программу, которая собирает входящие письма из почтового ящика #
# ========================================================================== #

driver = webdriver.Chrome()
driver.get('https://mail.ru/')

# авторизация на сайте mail.ru
"""
<input autocomplete="username" class="email-input svelte-1eyrl7y" type="text" 
    name="login" placeholder="Имя ящика" data-testid="login-input">
"""
elem = driver.find_element_by_name('login')
elem.send_keys('study.ai_172@mail.ru')
elem.send_keys(Keys.ENTER)

"""
<input placeholder="Пароль" name="password" class="password-input svelte-1eyrl7y" 
    type="password" autocomplete="current-password" data-testid="password-input">
"""
time.sleep(2)  # selenium.common.exceptions.ElementNotInteractableException: Message: element not interactable

elem = driver.find_element_by_name('password')
elem.send_keys('NextPassword172')
elem.send_keys(Keys.ENTER)

# Собираем ссылки на почтовые сообщения
"""
<a class="llc js-tooltip-direction_letter-bottom js-letter-list-item llc_normal"
    href="/inbox/0:16160864121691405336:0/?back=1&amp;afterReload=1"
    tabindex="-1" data-id="0:16160864121691405336:0" data-draggable-id="0:16160864121691405336:0"
    data-uidl-id="16160864121691405336" xpath="1">
"""
items = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "llc")))

i = 0
mails = []
link_texts = []
for item in items:
    link = item.get_attribute('data-uidl-id')
    link_text = '//a[@data-uidl-id="' + link + '"]'
    link_texts.append(link_text)

for link_text in link_texts:
    mail = {}
    print(i)
    i += 1
    try:
        # Открываем письмо и собираем необходимую информацию
        item_link = driver.find_element_by_xpath(link_text)
        item_link.click()
        time.sleep(delay)

        # <h2 class="thread__subject" xpath="1">Вход с нового устройства в аккаунт</h2>
        title = driver.find_element_by_tag_name('h2').text

        # <span class ="letter-contact" title="security@id.mail.ru" xpath="1">Mail.ru</span>
        letter_contact = driver.find_element_by_xpath('//span[@class="letter-contact"]').get_attribute('title')

        # <div class ="letter__date" xpath="1">Вчера, 21:53</div>
        letter_date = driver.find_element_by_xpath('//div[@class ="letter__date"]').text

        mail['contact'] = letter_contact
        mail['date'] = letter_date  # Можно написать функцию приведения даты к нормальному виду
        mail['title'] = title
        try:
            letter_body = driver.find_element_by_xpath('//div[contains(@id, "BODY")]').text
            mail['body'] = letter_body
        except BaseException:
            pass

        mails.append(mail)
    except BaseException:
        pass

    driver.back()
    time.sleep(delay)


driver.quit()  # Закрываем selenium (аналог нажатия крестик у окна chrom-а)


# ================================ #
# 2. Сложить собранные данные в БД #
# ================================ #

def mongo_insert_unique(documents):
    """
    Добавление нового документа в коллекцию c предварительной проверкой на его наличие в ней
    (проверка дублирования записей).

    Parameters:
    ----------
    documents: dict
        Документ который необходимо добать в коллекцию.

    """
    for news in documents:
        collection.update(news, news, upsert=True)


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

    for news in result:
        pprint(news)


# ================================================= #
# Работаем с MongoDB. Подключение к БД news_db #
# ================================================= #
db_name = 'mail_db'
client = MongoClient('localhost', 27017)
db = client[db_name]
collection = db.mail_collection

# fields = {'_id': True, 'name': True, 'link': True, 'date': True, 'source': True}
fields = {}  # Просматриваем все поля

# =================================================================== #
# Очищаем коллекцию (при необходимости, если не надо закоментировать) #
# =================================================================== #
# collection.delete_many({})

# =================================================================== #
# Добавляем записи в базу. Осуществляем проверку дублирования записей #
# =================================================================== #
print('\n---------\n2 задание\n---------')
mongo_insert_unique(mails)  # Проверка дублирования записей

# Показываем документы коллекции
mongo_brows(fields)

