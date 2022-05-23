import time
import logging
import os

import requests
import telegram

from dotenv import load_dotenv

import exceptions

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN', None)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', None)
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', None)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    try:
        logging.info(f'Сообщение успешно отправлено.')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except requests.exceptions.RequestException as error:
        logging.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Запрашиваем данные с сервера Практикума."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as erro:
        logging.error(f'Сервер Яндекс.Практикум вернул ошибку: {erro}')
    else:
        if response.status_code != 200:
            raise exceptions.EndpoinNotAvailable('Неверный статус код')
    return response.json()


def check_response(response):
    """Проверяем ответ сервера"""
    logging.debug('Проверка ответа сервера.........')
    if len(response) == 0:
        raise exceptions.EmptyResponse('Пустой респонс')
    if not isinstance(response, dict):
        raise TypeError('Респонс не является словарем')
    if 'homeworks' not in response.keys():
        raise Exception('Нет homeworks в ключах')
    if not isinstance(response.get('homeworks'), list):
        raise Exception('list')
    if not response:
        raise Exception('response is empty')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекаем из информации о конкретной домашней работе статус этой работы."""
    if len(homework) != 0:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        logging.debug(f'Домашка {homework_name} извлечена')
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        if homework['status'] is None:
            raise Exception(f'Статус unknown')
            logging.error(f'{error}')
        if homework_status != homework.get('status'):
            raise Exception(f'Ошибка доступа по ключу status')


def check_tokens():
    """Проверям доступность переменных окружения."""
    try:
        if (PRACTICUM_TOKEN is None) and (TELEGRAM_TOKEN is None) and (TELEGRAM_CHAT_ID is None):
            raise Exception('Failed because token is not set.')
    except Exception as error:
        logging.critical(f'Ошибка, не задан токен в качетсве переменнох окружения: {error}')
        return False
    else:
        return True
 

def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    tokens = check_tokens()
    response = get_api_answer(current_timestamp)
    homework = check_response(response)
    message = parse_status(homework)
    while True:
        try:
            
            if tokens is False:
                raise Exception('Ошибка в if tokens is False')
            
            # if not response:
            #    raise Exception('Ошибка  в if not response')
            
            # if type(checked) != list:
            #     raise Exception('Ошибка в if type(checked) != list')
            current_timestamp = ...
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
        else:
            send_message(bot, message)
        
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
