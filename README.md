# Homework_bot
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=ffffff&color=043A6B)](https://www.python.org/)
.. image:: https://img.shields.io/pypi/v/python-telegram-bot-raw.svg
   :target: https://pypi.org/project/python-telegram-bot-raw/
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/python-telegram-bot-raw.svg
   :target: https://pypi.org/project/python-telegram-bot-raw/
   :alt: Supported Python versions
[python-telegram-bot](https://python-telegram-bot.org)

## Описание проекта
Python Telegram Bot для проверки статуса проекта, который обращается к API сервиса Практикум.Домашка 

У API Практикум.Домашка есть лишь один эндпоинт: https://practicum.yandex.ru/api/user_api/homework_statuses/ и доступ к нему возможен только по токену.
Получить токен можно по адресу: https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a.
Принцип работы API
Когда ревьюер проверяет проект, он присваивает ей один из статусов: 
работа принята на проверку,
работа возвращена для исправления ошибок,
работа принята.
Если работа уже отправлена, но ревьюер пока не взял её на проверку, то это значит, что никакого статуса ей ещё не присвоено. 
С помощью API можно получить список проектов, с актуальными статусами за период от from_date до настоящего момента. История смены статусов через API недоступна: новый статус всегда перезаписывает старый.

## Что делает бот
- Раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
- При обновлении статуса анализирует ответ API и отправляет уведомление в Telegram;
- Логирует и сообщать о важных проблемах сообщением в Telegram.

## Запуск проекта
- Клонируйте репозиторий и перейдите в папку проекта:
```
git clone git@github.com:kaspeya/homework_bot.git
```
- Установите и активируйте виртуальное окружение:
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt:
```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
- Записать в переменные окружения (файл .env) необходимые ключи:
```bash
токен профиля на Яндекс.Практикуме
токен телеграм-бота
свой ID в телеграме
```

- Запустить проект
```bash
python homework.py
```

Автор: [Елизавета Шалаева](https://github.com/kaspeya)
