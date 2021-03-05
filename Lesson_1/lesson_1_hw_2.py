# Методы сбора и обработки данных из сети Интернет
# Соковнин Игорь Леонидович
#
# Урок 1. Основы клиент-серверного взаимодействия. Парсинг API
# Задание 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
# API вконтакте (https://vk.com/dev/first_guide).

import json
import requests
from pprint import pprint

# Возвращаем расширенную информацию о пользователях.
# https://api.vk.com/method/users.get?user_ids=507572987&fields=bdate&access_token=<token>&v=5.130

main_link = 'https://api.vk.com/method/users.get'
params = {'v': '5.130',
          'access_token': '<token>',
          'user_ids':'507572987',
          #'user_ids':'84953965',
          'fields': 'bdate'}

r = requests.get(main_link, params=params)
print(f'\nКод овета: {r.status_code}')
if r.ok:
    print('Расширенная информацию о пользователе:')
    #pprint(r.json())
    #pprint(r.json().get("response"))
    print('- ' + r.json().get("response")[0].get("first_name") + ' ' + r.json().get("response")[0].get("last_name"))
    with open('lesson1_hw_2_user.json', 'w', encoding='utf-8') as file:
        json.dump(r.json(), file, indent=2, ensure_ascii=False)
else:
    pass
"""
Код овета: 200
Расширенная информацию о пользователе:
- Игорь Соковнин

{'response': [{'bdate': '20.9.1969',
               'can_access_closed': True,
               'first_name': 'Игорь',
               'id': 507572987,
               'is_closed': False,
               'last_name': 'Соковнин'}]}
"""

# Возвращает список сообществ указанного пользователя.
# https://api.vk.com/method/groups.get?user_ids=507572987&extended=1&fields=bdate&access_token=<token>&v=5.130
main_link = 'https://api.vk.com/method/groups.get'
params = {'v': '5.130',
          'access_token': '<token>',
          'user_id': '507572987',
          # 'user_id': '84953965',
          'extended': '1'
          }
r = requests.get(main_link, params=params)
print(f'\nКод овета: {r.status_code}')
if r.ok:
    response = r.json()
    # pprint(response)
    # pprint(response.get("response"))
    # pprint(response.get("response").get("items")[1])
    # pprint(response.get("response").get("items")[1]["name"])
    try:
        # Сохраняем JSON-вывод в файле *.json
        with open('lesson1_hw_2_items.json', 'w', encoding='utf-8') as file:
            json.dump(response, file, indent=2, ensure_ascii=False)

        print('Возвращает список сообществ пользователя:')
        for repo in response.get("response").get("items"):
            print(f'- {repo.get("name")}')
    except ValueError:
        print('Ошибка сохранения json')
else:
    pass
"""
Код овета: 200
Возвращает список сообществ пользователя:
- Машинное обучение, AI, нейронные сети, Big Data
- Всё о 3D-принтерах и 3D-печати
- Центр робототехники и интеллектуальных систем
- Ардуино Arduino Пермь
- KARPOV.COURSES
- Основы интеллектуальных систем, компьютерного зр
- Занимательная робототехника
- GeekBrains
- OTUS. Онлайн-образование
- Python Programming
- Веб-стандарты
- Python 3.9 | ЯПрограммист
- Linux | Линукс
- Сетевой ИТ-Университет
- Raspberry Pi
- РобоМетод  | Робототехника для учителей
- Лаборатория 3D-моделирования ПГНИУ
- «Мозг. Вторая вселенная» в поддержку YN-2019
- Математика и междисциплинарные исследования
"""
