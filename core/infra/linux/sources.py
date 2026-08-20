
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import psutil

from core.domain.common.enum import SourceStatus
from core.domain.common.error import SourceReadError
from core.domain.models.monitor_data import MonitorData
from core.domain.ports.data_source import DataSource
from core.domain.value_objects.source_config import SourceConfig
from core.domain.value_objects.source_id import SourceId


class BaseLinuxSource(DataSource):
    """
    Базовая реализация Linux-источника.

    Хранит общую конфигурацию и предоставляет
    вспомогательные методы для создания MonitorData.
    """

    def __init__(
        self,
        source_id: str,
        name: str,
        interval: float,
    ) -> None:
        self._source_id = SourceId(source_id)

        self._config = SourceConfig(
            name=name,
            interval=interval,
        )

    @property
    def source_id(self) -> SourceId:
        return self._source_id

    @property
    def config(self) -> SourceConfig:
        return self._config

    def _success(
        self,
        value: str,
    ) -> MonitorData:
        """
        Создать успешный результат мониторинга.
        """

        return MonitorData(
            source_id=self.source_id,
            value=value,
            status=SourceStatus.OK,
            timestamp=datetime.now(),
        )

    def _error(
        self,
        error: Exception | str,
    ) -> MonitorData:
        """
        Создать результат с ошибкой.
        """

        return MonitorData(
            source_id=self.source_id,
            value="Недоступно",
            status=SourceStatus.ERROR,
            timestamp=datetime.now(),
            error=str(error),
        )


class PingSource(BaseLinuxSource):
    """
    Проверяет доступность 8.8.8.8 и отображает время ответа.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="ping",
            name="Ping",
            interval=1.0,
        )

    def read(self) -> MonitorData:
        try:
            result = subprocess.run(
                [
                    "ping",
                    "-c",
                    "1",
                    "-W",
                    "1",
                    "8.8.8.8",
                ],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

            if result.returncode != 0:
                raise SourceReadError(
                    "Узел 8.8.8.8 недоступен"
                )

            for line in result.stdout.splitlines():
                if "time=" in line:
                    value = (
                        line
                        .split("time=", 1)[1]
                        .split()[0]
                    )

                    return self._success(
                        f"{value} ms"
                    )

            raise SourceReadError(
                "Не удалось определить время ответа"
            )

        except Exception as exc:
            return self._error(exc)


class CpuUsageSource(BaseLinuxSource):
    """
    Использование CPU.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="cpu",
            name="CPU Usage",
            interval=1.0,
        )

    def read(self) -> MonitorData:
        try:
            usage = psutil.cpu_percent(
                interval=None
            )

            return self._success(
                f"{usage:.1f}%"
            )

        except Exception as exc:
            return self._error(exc)


class CpuTemperatureSource(BaseLinuxSource):
    """
    Температура CPU.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="temperature",
            name="CPU Temperature",
            interval=2.0,
        )

    def read(self) -> MonitorData:
        try:
            temperatures = (
                psutil.sensors_temperatures()
            )

            values: list[float] = []

            for entries in temperatures.values():
                for entry in entries:
                    if entry.current is not None:
                        values.append(
                            entry.current
                        )

            if not values:
                raise SourceReadError(
                    "Датчик температуры недоступен"
                )

            temperature = max(values)

            return self._success(
                f"{temperature:.1f} °C"
            )

        except Exception as exc:
            return self._error(exc)


class FanSpeedSource(BaseLinuxSource):
    """
    Скорость вращения вентиляторов.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="fan",
            name="Fan Speed",
            interval=2.0,
        )

    def read(self) -> MonitorData:
        try:
            fans = psutil.sensors_fans()

            values: list[int] = []

            for entries in fans.values():
                for entry in entries:
                    if entry.current is not None:
                        values.append(
                            entry.current
                        )

            if not values:
                raise SourceReadError(
                    "Датчики вентиляторов недоступны"
                )

            speed = max(values)

            return self._success(
                f"{speed} RPM"
            )

        except Exception as exc:
            return self._error(exc)


class RamUsageSource(BaseLinuxSource):
    """
    Использование оперативной памяти.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="ram",
            name="RAM Usage",
            interval=1.0,
        )

    def read(self) -> MonitorData:
        try:
            memory = psutil.virtual_memory()

            used_gb = (
                memory.used / 1024**3
            )

            total_gb = (
                memory.total / 1024**3
            )

            return self._success(
                (
                    f"{memory.percent:.1f}% "
                    f"({used_gb:.2f} / "
                    f"{total_gb:.2f} GB)"
                )
            )

        except Exception as exc:
            return self._error(exc)


class DiskUsageSource(BaseLinuxSource):
    """
    Использование корневого раздела.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="disk",
            name="Disk Usage",
            interval=5.0,
        )

    def read(self) -> MonitorData:
        try:
            disk = psutil.disk_usage("/")

            used_gb = (
                disk.used / 1024**3
            )

            total_gb = (
                disk.total / 1024**3
            )

            return self._success(
                (
                    f"{disk.percent:.1f}% "
                    f"({used_gb:.2f} / "
                    f"{total_gb:.2f} GB)"
                )
            )

        except Exception as exc:
            return self._error(exc)


class NetworkSpeedSource(BaseLinuxSource):
    """
    Скорость входящего и исходящего сетевого трафика.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="network",
            name="Network Speed",
            interval=1.0,
        )

        self._previous_counters = (
            psutil.net_io_counters()
        )

        self._previous_time = (
            time.monotonic()
        )

    def read(self) -> MonitorData:
        try:
            current_counters = (
                psutil.net_io_counters()
            )

            current_time = (
                time.monotonic()
            )

            elapsed = (
                current_time
                - self._previous_time
            )

            if elapsed <= 0:
                elapsed = 0.001

            download_speed = (
                current_counters.bytes_recv
                - self._previous_counters.bytes_recv
            ) / elapsed

            upload_speed = (
                current_counters.bytes_sent
                - self._previous_counters.bytes_sent
            ) / elapsed

            self._previous_counters = (
                current_counters
            )

            self._previous_time = (
                current_time
            )

            return self._success(
                (
                    f"↓ {download_speed / 1024:.1f} KB/s | "
                    f"↑ {upload_speed / 1024:.1f} KB/s"
                )
            )

        except Exception as exc:
            return self._error(exc)


class LoadAverageSource(BaseLinuxSource):
    """
    Load Average Linux за 1, 5 и 15 минут.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="load",
            name="Load Average",
            interval=2.0,
        )

    def read(self) -> MonitorData:
        try:
            load_1, load_5, load_15 = (
                os.getloadavg()
            )

            return self._success(
                (
                    f"1m: {load_1:.2f} | "
                    f"5m: {load_5:.2f} | "
                    f"15m: {load_15:.2f}"
                )
            )

        except Exception as exc:
            return self._error(exc)


class UptimeSource(BaseLinuxSource):
    """
    Время работы системы.
    """

    def __init__(self) -> None:
        super().__init__(
            source_id="uptime",
            name="Uptime",
            interval=5.0,
        )

    def read(self) -> MonitorData:
        try:
            uptime_seconds = int(
                time.time()
                - psutil.boot_time()
            )

            days, remainder = divmod(
                uptime_seconds,
                86400,
            )

            hours, remainder = divmod(
                remainder,
                3600,
            )

            minutes, _ = divmod(
                remainder,
                60,
            )

            return self._success(
                (
                    f"{days} д. "
                    f"{hours} ч. "
                    f"{minutes} мин."
                )
            )

        except Exception as exc:
            return self._error(exc)


class UsbFileSource(BaseLinuxSource):
    """
    Считывает 20 байт из файла на USB.
    """

    def __init__(
        self,
        file_path: str = "/media/usb/data.bin",
    ) -> None:
        super().__init__(
            source_id="usb",
            name="USB File",
            interval=1.0,
        )

        self._file_path = Path(
            file_path
        )

        self._position = 0

    def read(self) -> MonitorData:
        try:
            if not self._file_path.is_file():
                raise SourceReadError(
                    (
                        "USB-файл не найден: "
                        f"{self._file_path}"
                    )
                )

            file_size = (
                self._file_path.stat().st_size
            )

            if file_size == 0:
                raise SourceReadError(
                    "USB-файл пуст"
                )

            if self._position >= file_size:
                self._position = 0

            with self._file_path.open(
                "rb"
            ) as file:
                file.seek(
                    self._position
                )

                data = file.read(20)

                self._position = (
                    file.tell()
                )

            # Если достигли конца файла,
            # следующий вызов начнёт чтение сначала.
            if not data:
                self._position = 0

                with self._file_path.open(
                    "rb"
                ) as file:
                    data = file.read(20)

                    self._position = (
                        file.tell()
                    )

            return self._success(
                data.hex(" ")
            )

        except Exception as exc:
            return self._error(exc)