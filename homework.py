import logging
import os
import time
from typing import Dict

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (EmptyHomeworkException, EmptyResponseException,
                        NoKeyInHomeworkException, NoKeyInResponseException,
                        StatusCodeException, WrongKeyTypeResponseException,
                        WrongRecordHomeworkException,
                        WrongStatusInHomeworkException,
                        WrongTypeResponseException, YandexRequestException)

load_dotenv()

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

EXCEPTION_TO_STR = {
    YandexRequestException: 'API Яндекс Практикум недоступен',
    StatusCodeException: 'Сбой API Яндекс Практикум, неверный статус код',
    EmptyResponseException: 'Пустой ответ от API Яндекс',
    WrongTypeResponseException: 'Неверный тип ответа от API Яндекс',
    NoKeyInResponseException: 'Отсутствие нужных ключей от API Яндекс',
    WrongKeyTypeResponseException: 'Неподходящий тип ответа от API Яндекс',
}

HOMEWORK_EXCEPTIONS_TO_STR = {
    WrongRecordHomeworkException: 'Неправильная запись ДЗ',
    EmptyHomeworkException: 'Пустая запись ДЗ',
    NoKeyInHomeworkException: 'Нет нужного ключа в записи ДЗ',
    WrongStatusInHomeworkException: 'Неизвестный статус в записи ДЗ',
}


def check_tokens():
    """Проверям доступность переменных окружения."""
    try:
        if (PRACTICUM_TOKEN is None) \
                and (TELEGRAM_TOKEN is None) \
                and (TELEGRAM_CHAT_ID is None):
            raise Exception('Failed because token is not set.')
    except Exception as error:
        logging.critical(
            f'Ошибка, не задан токен в качетсве переменнох окружения: {error}'
        )
        return False
    else:
        return True


def send_message(bot, message):
    """Отправляем сообщение."""
    try:
        logging.info(f'Сообщение успешно отправлено. Сообщение: {message}')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except requests.exceptions.RequestException as error:
        logging.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Запрашиваем данные с сервера Практикума."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise StatusCodeException('Неверный статус код.')
    except requests.exceptions.RequestException as error:
        raise YandexRequestException(repr(error))
    return response.json()


def check_response(response):
    """Проверяем ответ сервера."""
    if not response:
        raise EmptyResponseException('Response is empty.')
    if not isinstance(response, dict):
        raise WrongTypeResponseException('Респонс не является словарем')
    if 'homeworks' not in response.keys():
        raise NoKeyInResponseException('Нет "homeworks" в ключах')
    if not isinstance(response.get('homeworks'), list):
        raise WrongKeyTypeResponseException('list')
    return response.get('homeworks')


def check_status(homework):
    """Проверяем статус ДЗ."""
    if not isinstance(homework, dict):
        raise WrongRecordHomeworkException('Неправильный тип записи ДЗ.')
    if len(homework) == 0:
        raise EmptyHomeworkException('Пустая запись ДЗ.')

    keys_required = ['homework_name']

    for key in keys_required:
        if key not in keys_required:
            raise NoKeyInHomeworkException(f'В записи о ДЗ нет ключа {key}.')

    hw_status = homework.get('status', 'unknown')
    hw_status_text = HOMEWORK_STATUSES.get(hw_status, 'unknown_text')

    if hw_status_text == 'unknown_text':
        raise WrongStatusInHomeworkException(
            f'Неизвестный статус ДЗ: {hw_status}.'
        )


def parse_status(homework):
    """Извлекаем из информации о конкретном ДЗ его статуc."""
    check_status(homework)
    homework_name = homework['homework_name']
    verdict = HOMEWORK_STATUSES[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def parse_hw_with_error(homework):
    """Обрабатываем ошибки при проверке ДЗ."""
    try:
        check_status(homework)
        return {**homework, 'error': 0}
    except WrongRecordHomeworkException as error:
        logging.error(
            HOMEWORK_EXCEPTIONS_TO_STR[WrongRecordHomeworkException],
            error)
        return {
            'error': HOMEWORK_EXCEPTIONS_TO_STR[WrongRecordHomeworkException]
        }
    except EmptyHomeworkException as error:
        logging.error(
            HOMEWORK_EXCEPTIONS_TO_STR[EmptyHomeworkException],
            error
        )
        return {
            'error': HOMEWORK_EXCEPTIONS_TO_STR[EmptyHomeworkException]
        }
    except NoKeyInHomeworkException as error:
        logging.error(
            HOMEWORK_EXCEPTIONS_TO_STR[NoKeyInHomeworkException],
            error
        )
        return {
            'error': HOMEWORK_EXCEPTIONS_TO_STR[NoKeyInHomeworkException]
        }
    except WrongStatusInHomeworkException as error:
        logging.error(
            HOMEWORK_EXCEPTIONS_TO_STR[WrongStatusInHomeworkException],
            error
        )
        homework['status'] = 'unknown'
        return {
            **homework,
            'error': HOMEWORK_EXCEPTIONS_TO_STR[WrongStatusInHomeworkException]
        }


def process_yandex_api():
    """Проверяем ошибки связанные с API Yandex."""
    current_timestamp = int(time.time())
    try:
        response_json = get_api_answer(current_timestamp)
        homeworks_list = check_response(response_json)
        homeworks_state_list = []
        for homework in homeworks_list:
            homework_state = parse_hw_with_error(homework)
            homeworks_state_list.append(homework_state)
        return {
            'global_error': 0,
            'homeworks_state': homeworks_state_list
        }
    except YandexRequestException as error:
        logging.error(EXCEPTION_TO_STR[YandexRequestException], error)
        return {
            'global_error': EXCEPTION_TO_STR[YandexRequestException],
            'homeworks_state': []
        }
    except StatusCodeException as error:
        logging.error(EXCEPTION_TO_STR[StatusCodeException], error)
        return {
            'global_error': EXCEPTION_TO_STR[StatusCodeException],
            'homeworks_state': []
        }
    except EmptyResponseException as error:
        logging.error(EXCEPTION_TO_STR[EmptyResponseException], error)
        return {
            'global_error': EXCEPTION_TO_STR[EmptyResponseException],
            'homeworks_state': []
        }
    except WrongTypeResponseException as error:
        logging.error(EXCEPTION_TO_STR[WrongTypeResponseException], error)
        return {
            'global_error': EXCEPTION_TO_STR[WrongTypeResponseException],
            'homeworks_state': []
        }
    except NoKeyInResponseException as error:
        logging.error(EXCEPTION_TO_STR[NoKeyInResponseException], error)
        return {
            'global_error': EXCEPTION_TO_STR[NoKeyInResponseException],
            'homeworks_state': []
        }
    except WrongKeyTypeResponseException as error:
        logging.error(EXCEPTION_TO_STR[WrongKeyTypeResponseException], error)
        return {
            'global_error': EXCEPTION_TO_STR[WrongKeyTypeResponseException],
            'homeworks_state': []
        }


def process_homework_changes(new_hw_state, homeworks_storage):
    """Обрабатываем изменения в ДЗ."""
    msg_list = []
    if new_hw_state["error"] != 0 and new_hw_state.get(
            'homework_name', None) is None:
        msg_list.append(
            f'Получили неизвестную домашку с ошибкой {new_hw_state["error"]}')
    else:
        # Сначала найдем соответствующую домашку в старых записях,
        # соответствие по ключу 'homework_name'
        old_hw_state_founded = homeworks_storage['homeworks_state'].get(
            new_hw_state['homework_name'],
            dict()
        )
        new_homework_name = new_hw_state['homework_name']
        # Если old_hw_state_founded остался пустым - значит новая домашка,
        # добавляем её к старым
        if len(old_hw_state_founded) == 0:
            # Записываем в сторадж новую домашку

            homeworks_storage[
                'homeworks_state'][new_homework_name] = new_hw_state
            msg_list.append(
                f'На проверке новая домашка: {new_hw_state["homework_name"]}')

            # Если новая домашка с неизвестным статусом - сообщить об ошибке
            if new_hw_state['status'] == 'unknown':
                msg_list.append(
                    f'Новый статус домашки'
                    f' {new_hw_state["homework_name"]} не определён!')
            return homeworks_storage, msg_list

        if new_hw_state['status'] != old_hw_state_founded['status']:
            msg_list.append(
                f'Изменился статус проверки работы'
                f' "{new_hw_state["homework_name"]}".'
                f'{HOMEWORK_STATUSES[new_hw_state["status"]]}')
            if new_hw_state['status'] == "unknown":
                msg_list.append(
                    f'Неопределённый статус домашки:'
                    f' {new_hw_state["homework_name"]}.')

            homeworks_storage['homeworks_state'][new_homework_name] =\
                new_hw_state
    return homeworks_storage, msg_list


def control_state(new_homeworks_state, homeworks_storage):
    """Основная логика работы бота."""
    if new_homeworks_state['global_error'] == \
            homeworks_storage['global_error']:
        if new_homeworks_state['global_error'] != 0:
            logging.debug('Статус не изменился: Глобальная ошибка')
            return [homeworks_storage, []]

    else:
        if new_homeworks_state['global_error'] != 0:
            homeworks_storage['global_error'] =\
                new_homeworks_state['global_error']
            return [
                homeworks_storage,
                [f'Global error {homeworks_storage["global_error"]}']
            ]
        homeworks_storage['global_error'] = 0

    hw_messages_list = []
    # Пробегаемся по каждой записи в листе новых домашек
    # (new_homeworks_state['homeworks_state'])
    for new_hw_state in new_homeworks_state['homeworks_state']:
        homeworks_storage, msg_list = process_homework_changes(
            new_hw_state=new_hw_state, homeworks_storage=homeworks_storage)
        hw_messages_list += msg_list

    if len(hw_messages_list) == 0:
        logging.debug('Статус не изменился.')

    return homeworks_storage, hw_messages_list


def bot_startup(homework_storage: Dict) -> Dict:
    """Заполняем словарь с ДЗ, с которым впоследствии будем сравнивать."""
    new_hw_state = process_yandex_api()
    homework_storage, _ = control_state(
        new_homeworks_state=new_hw_state,
        homeworks_storage=homework_storage
    )
    return homework_storage


def bot_process(homework_storage: Dict, bot) -> Dict:
    """Перезаписываем словарь с ДЗ, с которым впоследствии будем сравнивать."""
    new_hw_state = process_yandex_api()
    homework_storage, message_list = control_state(
        new_homeworks_state=new_hw_state,
        homeworks_storage=homework_storage
    )
    for message in message_list:
        send_message(bot, message)
    return homework_storage


def main():
    """Делаем запрос каждые 10 мин в бесконечном цикле."""
    homework_storage: Dict = {
        'global_error': 0,
        'homeworks_state': dict()
    }

    if not check_tokens():
        return

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    homework_storage = bot_startup(homework_storage)

    while True:
        time.sleep(RETRY_TIME)
        homework_storage = bot_process(homework_storage, bot)
