class IncorrectResponseException(TypeError):
    """Ответ API не соответствует ожидаемому типу."""
    pass


class UnknownStatusException(KeyError):
    """В ответе не обнаружены ожидаемые ключи."""
    pass


class TelegramApiException(Exception):
    """Telegram API не вернул ответ."""
    pass


class HomeworkMissingException(Exception):
    """В ответе API домашки нет ключа `homework_name`."""
    pass


class ApiUnknownException(Exception):
    """"Ошибка при запросе к API."""
    pass


class ApiResponseException(Exception):
    """Ответ API не соответствует ожидаемому."""
    pass


class EndpointUnavailableException(Exception):
    """Эндпоинт не доступен."""
    pass

class SendMessageException(Exception):
    """Ошибка при отправке сообщения."""
    pass
