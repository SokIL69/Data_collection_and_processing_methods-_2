# -*- coding: utf-8 -*-
import scrapy
import re  # Работа с регулярными выражениями
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'SokIL69'
    inst_pass = '#PWD_INSTAGRAM_BROWSER:9:1617340354:AVdQAMvLxkUqGyKExYORKTIBQ26AgXisbnoSj8FKv0djEL4rJ/jgo0XQVDPsXjqnf5EKUZiKRW47cVYobi6fJuuFSVpHXUGwq/KZ4BjYysCIMdNe8Jro2qOSLEzp6y/Est1tB/1FVwyWId0Wltaz'
    parse_users = ['wecodeinpython', 'know_datascience']  # имя профиля нужного пользователя (https://www.instagram.com/wecodeinpython/, https://www.instagram.com/know_datascience/)
    # parse_users = ['geekbrains.ru','ai_machine_learning']  # имя профиля нужного пользователя (https://www.instagram.com/geekbrains.ru/, https://www.instagram.com/ai_machine_learning/)
    graphql_url = 'https://www.instagram.com/graphql/query/'
    posts_hash = {
        # 'posts_hash': '42d2750e44dbac713ff30130659cd891'  # публикации
        'followers_hash': '5aefa9893005572d237da5068082d8d5',  # Подписчики
        'following_hash': '3dec7e2c57367ef3da3d987d89f9dbc8'   # Подписки
    }
    # публикации
    # GET https://www.instagram.com/graphql/query/?query_hash=42d2750e44dbac713ff30130659cd891
    #    &variables={"id":"7709057810", "first":12,
    #                "after":"QVFCY1JRYXYzWWp6c0xBamR0c3NoaW5uWFhEbXZVb21DRGNCQVhySG9CV3F0VEFZcUNfUWxESnhLVDhseUhkV0ZXRzh3ZXF2eUhxSzdqdDlNTmlnX2V3Mg=="}
    # GET https://www.instagram.com/graphql/query/?query_hash=42d2750e44dbac713ff30130659cd891&variables={"id":"6709301740","first":12}

    # Подписчики
    # GET https://www.instagram.com/graphql/query/?query_hash = 3dec7e2c57367ef3da3d987d89f9dbc8
    #    &variables={"id": "37238354748", "include_reel": true, "fetch_mutual": false, "first": 24}
    # GET https://www.instagram.com/graphql/query/?query_hash = 3dec7e2c57367ef3da3d987d89f9dbc8
    #    &variables={"id": "37238354748", "include_reel": true, "fetch_mutual": false, "first": 12,
    #                  "after": "QVFCUFNDa3VYSENUMkNna0xrZzN4TW11WGNELU1HRmpxZzNHdG1pZWFadGV4a192ZVh1RTZkdjkzRGszRjRBamx6QVE2NUtLbVpnblVNUnJnelBsS3B0eA=="}

    # Подписки
    # GET https://www.instagram.com/graphql/query/?query_hash=5aefa9893005572d237da5068082d8d5
    #    &variables={"id": "37238354748", "include_reel": true, "fetch_mutual": true, "first": 24}
    # GET https://www.instagram.com/graphql/query/?query_hash = 5aefa9893005572d237da5068082d8d5
    #    &variables={"id": "37238354748", "include_reel": true, "fetch_mutual": false, "first": 12,
    #    "after": "QVFCX01WcVU1elZDZVRETVJCTDJmLWM1WlFhUUdndWZibkcxaTd6Y283U01lLUtuWDJHMU0tbjVvWm84T1IzR01QenZjQkZJX0Nack1qLTIzTnNZOC1NYQ=="}

    def parse(self, response:HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        # Делаем запрос с отправкой данных из формы
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_login,  # 1
            formdata={'username': self.inst_login, 'enc_password':self.inst_pass, 'queryParams': {}, 'optIntoOneTap': 'false'},
            headers={'X-CSRFToken': csrf_token}
        )

    # 1
    def user_login(self, response:HtmlResponse):
        j_body = response.json()
        if j_body.get('authenticated'):
            for user in self.parse_users:
                yield response.follow(  # Сохраняем текущую сессию
                    f'/{user}',
                    callback=self.user_data_parse,  # 2
                    cb_kwargs={'username': user}  # имя пользователя с которым мы в данный момент работаем (56:22)
                )

    # 2
    # Обследование html-кода
    def user_data_parse(self, response:HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 12}

        for key, query_hash in self.posts_hash.items():
            url_posts = f'{self.graphql_url}?query_hash={query_hash}&{urlencode(variables)}'
            # Обработка публикаций, подписчиков, подписок
            yield response.follow(
                url_posts,
                callback=self.followers_following_parser,  # 3
                cb_kwargs={'variables': deepcopy(variables),
                           'username': username,
                           'user_id': user_id,
                           'target': deepcopy(key)}
            )

    # 3
    def followers_following_parser(self, response: HtmlResponse, variables, username, user_id, target):
        j_data = json.loads(response.text)
        if target == 'followers_hash':
            # Обработка подписчиков
            data_user = j_data.get('data').get('user').get('edge_followed_by')
        elif target == 'following_hash':
            # Обработка подписок
            data_user = j_data.get('data').get('user').get('edge_follow')

        page_info = data_user.get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
            url_posts = f'{self.graphql_url}?query_hash={self.posts_hash[target]}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.followers_following_parser,
                cb_kwargs={'variables': deepcopy(variables),
                           'username': username,
                           'user_id': user_id,
                           'target': target}
            )

        edges = data_user.get('edges')  # Список публикаций
        for edge in edges:
            # Собираем информацию о публикациях
            yield InstaparserItem(
                user_id=user_id,  # id пользователя которому принадлежит публикация
                id=edge.get('node').get('id'),
                user_name=edge.get('node').get('username'),
                full_name = edge.get('node').get('full_name'),
                photo=edge.get('node').get('profile_pic_url'),
                post_data=edge.get('node'),
                parse_user=username,
                target=target
            )

    # Получаем токен для авторизации (ищем token в ответе первого GET запроса)
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')


# graphql - Публикации: query_hash=42d2750e44dbac713ff30130659cd891
# GET https://www.instagram.com/graphql/query/?
# query_hash=42d2750e44dbac713ff30130659cd891
# &variables={
# "id":227709057810",  # id профиля parse_user = 'geekbrains.ru'
# "first":"12,
# "after":"QVFDbGoza05UQTNWaUk2N0w0aXhPQXRwOERXWnh5Szk2OVZnY3ZaSVJxMjNtbjZXdlUtbVNrTEExN25JR1JsUWJVT05aeUM3TlZHbWRpWHA5RThTVVhMSQ=="
# }
# GET
# https: // www.instagram.com / graphql / query /?query_hash = 42
# d2750e44dbac713ff30130659cd891 & variables = {"id": "7709057810", "first": 12,
#                                               "after": "QVFEMVctRlZOSjRfMENhU2hyb3JILWhXZnh3QWxrNVRUc3BTd3RSbHhqS01LQ01KcWNwTDJzem9XZWRGaU5CR2tkNzAxNjVzd3R3NHNIcVFOUUk0V2RIZA=="}
# response.text
# '{"user":true,"userId":"25364634079","authenticated":true,"oneTapPrompt":true,"reactivated":true,"status":"ok"}'


# https://www.instagram.com/accounts/login/ajax/

# Первый GET запрос
# Инспектор/ищем в html строку 'csrf'
# window._sharedData = {"config":{"csrf_token":"uCATOPozZHulxpnqSDpLvQQjM4O5vwA3", ...

# Заголовки
# X-CSRFToken W6K3iEOduubJp43PAxxCH97TSEcHbfTs

# Запрос:
# username	"SokIL69"
# enc_password	"#PWD_INSTAGRAM_BROWSER:10:1617253929:AWlQABRPsdjvNUbbRRNd7MMh82TikJkfOcwQGn1L+8Pce7VOi0HvqKBr1uVZ5kBfvrILrQzfLUc79VPej9U2Fv7AW+q2MQK5K8pvBVIXvROG3hAR6LNe0RO0LnYp/mZlY0yfJ8KdGnZGC9bin5li"
# queryParams	"{}"
# optIntoOneTap	"false"

# Ответ:
# user	true
# userId	"25364634079"
# authenticated	true
# oneTapPrompt	true
# reactivated	true
# status	"ok"

