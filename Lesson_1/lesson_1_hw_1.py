# Соковнин Игорь Леонидович
# Методы сбора и обработки данных из сети Интернет
#
# Урок 1. Основы клиент-серверного взаимодействия. Парсинг API
# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.
#
# https://docs.github.com/en/rest - GitHub API документация
# Информация о пользователе GitHub с логином USERNAME доступна по ссылке: https://api.github.com/users/USERNAME.

import json
import requests
from pprint import pprint

url = 'https://api.github.com/users/SokIl69/repos'
# url = 'https://api.github.com/users/octocat/repos'


# Получить все репозитории пользователя
repos = requests.get(url)
print(f'Код овета: {repos.status_code}')

if repos.ok:
    # Сохраняем JSON-вывод в файле *.json
    try:
        repo = repos.json()
        # pprint(repo)
        with open('lesson_1_hw_1.json', 'w', encoding='utf-8') as file:
            json.dump(repo, file, indent=2, ensure_ascii=False)
        # Выводим список репозиториев пользователя
        print('Список репозиториев пользователя:')
        for repo in repos.json():
            if not repo['private']:
                print(f"- {repo['html_url']}")
    except ValueError:
        print('Ошибка сохранения json')
else:
    pass

"""
Код овета: 200
Список репозиториев пользователя:
- https://github.com/SokIL69/common
- https://github.com/SokIL69/databases
- https://github.com/SokIL69/Datebases
- https://github.com/SokIL69/gbr
- https://github.com/SokIL69/python
- https://github.com/SokIL69/Python_for_Data_Science
- https://github.com/SokIL69/Python_for_Data_Science_2
- https://github.com/SokIL69/Sports-data-analysis-Kaggle-II
"""
