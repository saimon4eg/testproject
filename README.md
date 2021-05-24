# Тестовое задание

## Задание

Реализовать на Django Rest Framework RESTful API, позволяющее:

- Осуществлять create, read, delete операции с сообщениями
- Проставлять флаг "прочитано" сообщению
- Генерация csv-файла из всех сообщений или из ограниченного количества по параметрам фильтрации (на свое усмотрение).
  Формат: идентификатор, заголовок, тело, флаг отправки, флаг прочтения, датавремя создания. Сортировка в порядке
  создания.

При создании сообщения запускать celery задачу, которая проставит сообщению флаг "отправлено" (имитация отправки в
сторонний сервис). Ограничить количество допустимых запросов на создание сообщения в 10 запросов в минуту. При
превышении лимита отставать соответствующее сообщение со статусом 429 и писать лог в файл с информацией о запросе и
клиенте. По желанию банить запросы на создание с IP-адреса на 10 минут.

Структура сообщения (перечислены только критичные поля):

- заголовок
- тело сообщения
- флаг отправки
- флаг прочтения
- датавремя создания
- датавремя обновления

Ограничения:

- PEP8
- Аннотация типов (очень желательно)
- Необходимо использовать Django Rest Framework
- По СУБД ограничений нет. Можно даже SQLite
- Аутентификация с авторизацией - необязательно, по желанию
- Брокер сообщений - любой. RabbitMQ будет плюсом
- Тесты и документация - будут плюсом
- Плюсом будет обернуть приложение в docker контейнер и использовать docker-compose для оркестрации

## Установка

    cd ~
    git clone https://github.com/saimon4eg/testproject.git
    cd testproject
    chmod +x ./install_rabit.sh
    sudo ./install_rabit.sh
    sudo -H pip3 install --upgrade pip
    sudo -H pip3 install virtualenv
    virtualenv ../env
    source ../env/bin/activate
    pip install -r requirements.txt
    ./manage.py createsuperuser

## Запуск

В консоли №1 запускаем сервер Django

    cd ~/testproject
    source ../env/bin/activate
    ./manage.py runserver 0.0.0.0:8000

В консоли №2 запускаем Celery

    cd ~/testproject
    source ../env/bin/activate
    celery --app testproject worker --loglevel=debug --concurrency=4

## Использование

Работа с api разрешена только для авторизованных пользователей, авторизоваться можно на странице /api-auth/ используя
email / пароль который был указан при установке на последнем шаге. Создать новых пользователей можно тут
/admin/auth/user/add/. Любой пользователь может отправить сообщение любому пользователю, в том числе себе. Отправитель
может отредактировать сообщение, при этом у него снимается флаг read. Получатель может прочитать свои сообщения, при
этом сообщению устанавливается флаг read.

/messages/ - получить все сообщения пользователя, по умолчанию возвращаются входящие сообщения, если добавить GET
параметр outgoing=true то веернет исходящие сообщения.

/messages/csv/ - то же самое что и /messages/ (в том числе поддерживает параметр outgoing=true), но вернет csv файл.

/messages/create/ - создать сообщение

/messages/{id} - создать сообщение
