class IncorrectTypeResponseException(TypeError):
    """Ответ API не соответствует ожидаемому типу."""
    pass


class KeyIncorrectTypeException(TypeError):
    """Значение ключа `homeworks` не является типом `list`."""
    pass


class UnknownStatusException(KeyError):
    """В ответе не обнаружены ключи `current_date` или `homeworks`."""
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
