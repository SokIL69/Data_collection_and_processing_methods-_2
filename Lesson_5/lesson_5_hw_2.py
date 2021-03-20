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
from selenium import webdriver
from pprint import pprint
from pymongo import MongoClient


# chrom_options = Options()
# Раскрываем окно браузера на максимум
# chrom_options.add_argument('start-maximized')
# driver = webdriver.Chrome(options=chrom_options)

driver = webdriver.Chrome()
driver.get('https://www.mvideo.ru/')

# ===================================================== #
# 1. Написать программу, которая собирает «Хиты продаж» #
#    с сайта техники mvideo и складывает данные в БД    #
# ===================================================== #

"""
<a href="/products/smartfon-apple-iphone-12-mini-128gb-product-red-mge53ru-a-30052877" 
    class="fl-product-tile-picture fl-product-tile-picture__link" 
    data-product-info="{ &quot;
        productPriceLocal&quot;: &quot;73490.00&quot;, &quot;
        productId&quot;: &quot;30052877&quot;, &quot;
        productName&quot;: &quot;Смартфон Apple iPhone 12 mini 128GB (PRODUCT)RED (MGE53RU/A)&quot;, &quot;
        productCategoryId&quot;: &quot;cat2_cis_0000000357&quot;, &quot;
        productCategoryName&quot;: &quot;Смартфоны&quot;, &quot;
        productVendorName&quot;: &quot;Apple&quot;, &quot;
        productGroupId&quot;: &quot;cat1_cis_0000000012&quot;, &quot;
        Location&quot;: &quot;block5260655&quot;, &quot;eventPosition&quot;: 1} 
    data-ga-track="false" 
    data-track-event="click" 
    data-track-category="add_to_cart_pop_up" 
    data-track-action="cart_popup_acessories_product_photo_click" 
    data-track-label="Смартфон Apple iPhone 12 mini 128GB (PRODUCT)RED (MGE53RU/A)" 
    data-pushable="true" 
    data-action="click" 
    data-holder="#clickProductCard30052877_block5260655">
"""

item = driver.find_element_by_xpath('//div[contains(@class, "gallery-layout products")]')
btn_xpath = '//a[contains(@class, "next-btn c-btn c-btn_scroll-horizontal c-btn_icon i-icon-fl-arrow-right")]'

delay = 3
num_click = 5

# while True:
for i in range(num_click):
    try:
        button = item.find_element_by_xpath(btn_xpath)
        button.click()
    except BaseException:
        pass
    time.sleep(delay)

item = driver.find_element_by_xpath('//div[contains(@class, "gallery-layout products")]')

# В pyCharm не ищет '//div[contains(@class, "gallery-layout products") and contains(@xpath, "1")]
# //a[@class="fl-product-tile-picture fl-product-tile-picture__link"]'?
# , хотя на web-странице это строка находит нужные элементы

# <div class="h2 u-mb-0 u-ml-xs-20 u-hidden-tablet u-hidden-desktop gallery-layout__title u-font-normal" xpath="1">
#   Хиты продаж
# </div>

hits = item.find_elements_by_xpath('//div[contains(@class, "h2 u-mb-0 u-ml-xs-20 u-hidden-phone")]')
for hit in hits:
    print(hit.text)

items = driver.find_elements_by_xpath('//div[contains(@class, "gallery-layout products")]'
                                      '//li//a[@class="fl-product-tile-picture fl-product-tile-picture__link"]')

product_list = []
for item in items:
    prod = {}
    product = item.get_attribute('data-product-info')
    product = product.replace('\t', '').replace('{\n', '').replace('}', '').replace(' "', '')
    product = product.replace('"', '').replace(',', '').replace(':', '\n')
    s = product.split('\n')
    prod[s[0]] = float(s[1])
    prod[s[4]] = s[5]
    prod[s[8]] = s[9]

    product_list.append(prod)

""" [ 'productPriceLocal', '6990.00',
     'productId', '20064307',
     'productName', 'Мультиварка Redmond RMC-IHM303',
     'productCategoryId', 'cat2_cis_0000000284',
     'productCategoryName', 'Мультиварки',
     'productVendorName', 'Redmond',
     'productGroupId', 'cat1_cis_0000000003',
     'Location', 'block5260655',
     'eventPosition', ' 9']"""

pprint(product_list)

driver.quit()

