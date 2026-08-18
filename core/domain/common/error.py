class MonitoringError(Exception):
    """
    Базовое исключение Domain.
    """


class SourceReadError(MonitoringError):
    """
    Ошибка чтения данных источником.
    """