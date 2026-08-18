from abc import ABC, abstractmethod

from core.domain.models.monitor_data import MonitorData
from core.domain.value_objects.source_config import SourceConfig
from core.domain.value_objects.source_id import SourceId


class DataSource(ABC):
    """
    Абстракция источника данных.
    """

    @property
    @abstractmethod
    def source_id(self) -> SourceId:
        """
        Уникальный идентификатор источника.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def config(self) -> SourceConfig:
        """
        Конфигурация источника.
        """

        raise NotImplementedError

    @abstractmethod
    def read(self) -> MonitorData:
        """
        Получить текущее значение источника.
        """

        raise NotImplementedError