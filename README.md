# Криптоаналитика

Приложение для анализа роста/падения различных криптовалют

## Руководство по эксплуатации

- Из корня проекта стартуем команду ```docker compose up```
- Довольствуемся результатом

## Документация

### auth

Каталог с файлами для создания access и refresh токена для аутентификации.
Также содержит функции для этой самой аутентификации.

### certs

Каталог с приватным и публичным ключами, так как алгоритм RS256.

### database & alembic & alembic.ini & database.db

Каталоги с подключением к бд и моделью пользователя, а также для создания миграций. 
Также сам файл базы данных.

### templates

Каталог с базовыми html-страницами и файлом ```router.py```
В файле идет простое подключение html-страниц.

### test_main & pytest.ini

Внутри файл с API тестами.

В pytest.ini конфигурация для *pytest*.

### exchange_rate.py

Файл с взаимодействием с **Binance** API, а также вебсокетами и редисом.
В нем реализуются основные ручки приложения.

### config.py

Два класса с настройками JWT и бд для *Alembic*.

### main.py

Основной файл с созданием приложения, корсами и подключением роутеров.

## CI/CD

В пайплайне я добавил всего лишь две джобы: *build* и *test*.
deploy закоммичена, ибо некуда деплоить (да и на гитхаб раннере docker-compose нету).

## Примечание

[Ссылочка](https://crypt-lspx.onrender.com)
Но платный тариф может слететь, и сайт не будет доступен.

Можете распространять код, делать с ним что угодно, если будут вопросы, то вот почта:
```inksne@gmail.com```
