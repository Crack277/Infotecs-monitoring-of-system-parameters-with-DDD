from abc import ABC, abstractmethod

from core.domain.ports.data_source import DataSource


class SourceFactory(ABC):
    """
    Порт фабрики источников данных.
    """

    @abstractmethod
    def create_sources(self) -> list[DataSource]:
        """
        Создать набор источников мониторинга.
        """

        raise NotImplementedError