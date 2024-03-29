import logging
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (ApiResponseException, ApiUnknownException,
                        EndpointUnavailableException, HomeworkMissingException,
                        IncorrectTypeResponseException,
                        KeyIncorrectTypeException, SendMessageException,
                        UnknownStatusException)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

handler = RotatingFileHandler(
    'main.log',
    maxBytes=50000000,
    backupCount=5,
    encoding='UTF-8'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens_available = all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])
    logger.debug('Попытка проверить доступность переменных окружения')
    if not tokens_available:
        logger.critical(
            'Отсутствуют обязательные переменные '
            'окружения во время запуска бота'
        )
        return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.debug(f'Попытка отправки сообщения: {message}')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение {message} успешно отправлено')
    except Exception as error:
        error_message = f'Ошибка при отправке сообщения: {error}'
        logger.exception(error_message)
        raise SendMessageException(error_message) from error


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.debug('Попытка запросить ответ API')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except ConnectionRefusedError as error:
        error_message = f'Ресурс {ENDPOINT} недоступен: {error}'
        raise EndpointUnavailableException(error_message) from error
    except Exception as error:
        error_message = f'Ошибка при запросе к API: {error}'
        raise ApiUnknownException(error_message) from error
    if response.status_code == HTTPStatus.OK:
        logger.debug('Ответ API получен')
        return response.json()
    raise ApiResponseException(
        f'Код ответа API: `{response.status_code}` '
        f'при параметрах: `{params}`'
    )


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logger.debug('Проверка ответа сервиса на корректность')
    if not isinstance(response, dict):
        error_message = (
            'Ответ API не соответствует документации, '
            f'тип ответа является {type(response)} вместо dict'
        )
        raise IncorrectTypeResponseException(error_message)
    if ('current_date' not in response
       or 'homeworks' not in response):
        raise UnknownStatusException(
            'Ответ API: '
            f'{response}'
        )
    if not isinstance(response.get('homeworks'), list):
        homeworks_type = response.get('homeworks')
        raise KeyIncorrectTypeException(
            'Ответ API не соответствует документации. '
            'Значение ключа `homeworks`: '
            f'{type(homeworks_type)} вместо list'
        )
    return response.get('homeworks')


def parse_status(homework):
    """Извлекает из информации о домашней работе статус этой работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    logger.debug('Попытка извлечь информацию о статусе домашки')
    if homework_name is None:
        raise HomeworkMissingException(
            f'`homework_name` отсутствует: {homework_name}')
    if homework_status not in HOMEWORK_VERDICTS:
        error_message = (
            f'Получен неизвестный статус домашней работы: {homework_status}')
        raise UnknownStatusException(error_message)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise SystemExit('Критическая ошибка, бот остановлен')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time()) - RETRY_PERIOD
    last_error = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            else:
                logger.debug('Нет обновлений статусов домашних работ')
            current_timestamp = int(time.time())
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.exception(message)
            if last_error != error:
                try:
                    send_message(bot, message)
                except SendMessageException:
                    pass
                else:
                    last_error = error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
