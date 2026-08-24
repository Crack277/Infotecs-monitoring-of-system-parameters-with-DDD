from __future__ import annotations

import logging

from PySide6.QtCore import QThread, Slot
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.domain.common.enum import SourceStatus
from core.domain.models.monitor_data import MonitorData
from core.domain.ports.data_source import DataSource
from core.domain.ports.source_factory import SourceFactory
from core.infra.qt.worker import MonitorWorker


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Главное окно System Monitor.
    """

    def __init__(
        self,
        source_factory: SourceFactory,
    ) -> None:
        super().__init__()

        self._source_factory = source_factory

        self._sources: list[DataSource] = []
        self._threads: list[QThread] = []
        self._workers: list[MonitorWorker] = []

        self._value_labels: dict[str, QLabel] = {}
        self._status_labels: dict[str, QLabel] = {}

        self._is_monitoring = False

        self._setup_window()
        self._setup_ui()

    def _setup_window(self) -> None:
        self.setWindowTitle("System Monitor")
        self.resize(900, 650)

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        main_layout.setSpacing(15)

        # ---------- HEADER ----------

        header_layout = QHBoxLayout()

        title_label = QLabel("SYSTEM MONITOR")
        title_label.setObjectName("titleLabel")

        self._start_stop_button = QPushButton("Старт")
        self._start_stop_button.setObjectName("startButton")

        self._start_stop_button.clicked.connect(
            self._toggle_monitoring
        )

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(
            self._start_stop_button
        )

        main_layout.addLayout(header_layout)

        # ---------- MONITORING TABLE ----------

        grid_layout = QGridLayout()

        grid_layout.setSpacing(12)

        grid_layout.addWidget(
            QLabel("Источник"),
            0,
            0,
        )

        grid_layout.addWidget(
            QLabel("Значение"),
            0,
            1,
        )

        grid_layout.addWidget(
            QLabel("Статус"),
            0,
            2,
        )

        self._sources = (
            self._source_factory.create_sources()
        )

        for index, source in enumerate(
            self._sources,
            start=1,
        ):
            source_id = source.source_id.value

            name_label = QLabel(
                source.config.name
            )

            value_label = QLabel(
                "Остановлено"
            )

            status_label = QLabel(
                "STOPPED"
            )

            value_label.setObjectName(
                "valueLabel"
            )

            status_label.setObjectName(
                "statusStopped"
            )

            self._value_labels[source_id] = (
                value_label
            )

            self._status_labels[source_id] = (
                status_label
            )

            grid_layout.addWidget(
                name_label,
                index,
                0,
            )

            grid_layout.addWidget(
                value_label,
                index,
                1,
            )

            grid_layout.addWidget(
                status_label,
                index,
                2,
            )

        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 4)
        grid_layout.setColumnStretch(2, 1)

        main_layout.addLayout(grid_layout)

        main_layout.addStretch()

        self._setup_styles()

    def _setup_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1e1e1e;
            }

            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                padding: 8px;
            }

            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
            }

            QLabel#valueLabel {
                background-color: #2b2b2b;
                border-radius: 6px;
                font-family: monospace;
            }

            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#startButton {
                background-color: #2e7d32;
                color: white;
            }

            QPushButton#stopButton {
                background-color: #c62828;
                color: white;
            }

            QLabel#statusOk {
                color: #4caf50;
                font-weight: bold;
            }

            QLabel#statusError {
                color: #f44336;
                font-weight: bold;
            }

            QLabel#statusStopped {
                color: #9e9e9e;
                font-weight: bold;
            }
            """
        )

    @Slot()
    def _toggle_monitoring(self) -> None:
        """
        Переключить состояние мониторинга.
        """

        if self._is_monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()

    def _start_monitoring(self) -> None:
        """
        Запустить мониторинг.
        """

        if self._is_monitoring:
            return

        logger.info("Starting monitoring")

        self._threads.clear()
        self._workers.clear()

        for source_id, value_label in (
            self._value_labels.items()
        ):
            value_label.setText(
                "Ожидание данных..."
            )

            status_label = (
                self._status_labels[source_id]
            )

            status_label.setText(
                "WAITING"
            )

            status_label.setObjectName(
                "statusStopped"
            )

            self._refresh_widget_style(
                status_label
            )

        for source in self._sources:
            self._create_worker(source)

        self._is_monitoring = True

        self._start_stop_button.setText(
            "Стоп"
        )

        self._start_stop_button.setObjectName(
            "stopButton"
        )

        self._refresh_widget_style(
            self._start_stop_button
        )

    def _stop_monitoring(self) -> None:
        """
        Остановить мониторинг.
        """

        if not self._is_monitoring:
            return

        logger.info("Stopping monitoring")

        # Сначала просим Worker завершиться.
        for worker in self._workers:
            worker.stop()

        # Ждём завершения потоков.
        for thread in self._threads:
            if thread.isRunning():
                thread.wait(2000)

        self._threads.clear()
        self._workers.clear()

        self._is_monitoring = False

        self._start_stop_button.setText(
            "Старт"
        )

        self._start_stop_button.setObjectName(
            "startButton"
        )

        self._refresh_widget_style(
            self._start_stop_button
        )

        for source_id, value_label in (
            self._value_labels.items()
        ):
            value_label.setText("Остановлено")

            status_label = (
                self._status_labels[source_id]
            )

            status_label.setText("STOPPED")

            status_label.setObjectName(
                "statusStopped"
            )

            self._refresh_widget_style(
                status_label
            )

        logger.info("Monitoring stopped")

    def _create_worker(
        self,
        source: DataSource,
    ) -> None:
        """
        Создать QThread и Worker
        для одного источника.
        """

        thread = QThread(self)

        worker = MonitorWorker(
            source=source
        )

        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        worker.data_received.connect(
            self._on_data_received
        )

        worker.finished.connect(thread.quit)

        self._threads.append(thread)
        self._workers.append(worker)

        thread.start()

        logger.info(
            "Worker created: %s",
            source.config.name,
        )

    @Slot(object)
    def _on_data_received(
        self,
        data: MonitorData,
    ) -> None:
        """
        Получить данные от Worker.
        """

        source_id = data.source_id.value

        value_label = self._value_labels.get(
            source_id
        )

        status_label = self._status_labels.get(
            source_id
        )

        if value_label is None:
            logger.warning(
                "Unknown source: %s",
                source_id,
            )
            return

        value_label.setText(data.value)

        if status_label is None:
            return

        if data.status is SourceStatus.OK:
            status_label.setText("OK")
            status_label.setToolTip("")

            status_label.setObjectName(
                "statusOk"
            )

        else:
            status_label.setText("ERROR")

            status_label.setToolTip(
                data.error or "Неизвестная ошибка"
            )

            status_label.setObjectName(
                "statusError"
            )

        self._refresh_widget_style(
            status_label
        )

    @staticmethod
    def _refresh_widget_style(
        widget: QWidget,
    ) -> None:
        style = widget.style()

        style.unpolish(widget)
        style.polish(widget)

        widget.update()

    def closeEvent(self, event) -> None:
        """
        Корректно остановить мониторинг
        перед закрытием приложения.
        """

        self._stop_monitoring()

        event.accept()