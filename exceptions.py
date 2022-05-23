class YandexRequestException(Exception):
    pass


class StatusCodeException(ValueError):
    pass


class EmptyResponseException(Exception):
    pass


class WrongTypeResponseException(TypeError):
    pass


class NoKeyInResponseException(KeyError):
    pass


class WrongKeyTypeResponseException(TypeError):
    pass


class WrongRecordHomeworkException(TypeError):
    pass


class EmptyHomeworkException(ValueError):
    pass


class NoKeyInHomeworkException(KeyError):
    pass


class WrongStatusInHomeworkException(KeyError):
    pass
