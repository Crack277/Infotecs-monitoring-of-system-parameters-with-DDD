
import logging
import threading
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot

from core.domain.common.enum import SourceStatus
from core.domain.models.monitor_data import MonitorData
from core.domain.ports.data_source import DataSource


logger = logging.getLogger(__name__)


class MonitorWorker(QObject):
    """
    Worker для мониторинга одного источника.

    Каждый экземпляр работает
    внутри отдельного QThread.
    """

    data_received = Signal(object)
    finished = Signal()

    def __init__(
        self,
        source: DataSource,
    ) -> None:
        super().__init__()

        self._source = source
        self._stop_event = threading.Event()

    @Slot()
    def run(self) -> None:
        logger.info(
            "Worker started: %s",
            self._source.config.name,
        )

        try:
            while not self._stop_event.is_set():
                try:
                    data = self._source.read()

                except Exception as exc:
                    logger.exception(
                        "Unexpected error in source: %s",
                        self._source.config.name,
                    )

                    data = MonitorData(
                        source_id=(
                            self._source.source_id
                        ),
                        value="Недоступно",
                        status=SourceStatus.ERROR,
                        timestamp=datetime.now(),
                        error=str(exc),
                    )

                self.data_received.emit(data)

                self._stop_event.wait(
                    self._source.config.interval
                )

        finally:
            logger.info(
                "Worker stopped: %s",
                self._source.config.name,
            )

            self.finished.emit()

    def stop(self) -> None:
        self._stop_event.set()