
from enum import StrEnum


class SourceStatus(StrEnum):
    """
    Состояние источника данных.
    """
    
    OK = "ok"
    ERROR = "error"