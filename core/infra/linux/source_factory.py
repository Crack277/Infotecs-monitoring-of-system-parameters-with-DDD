from core.domain.ports.data_source import DataSource
from core.domain.ports.source_factory import SourceFactory

from core.infra.linux.sources import (
    CpuTemperatureSource,
    CpuUsageSource,
    DiskUsageSource,
    FanSpeedSource,
    LoadAverageSource,
    NetworkSpeedSource,
    PingSource,
    RamUsageSource,
    UptimeSource,
    UsbFileSource,
)


class LinuxSourceFactory(SourceFactory):
    """
    Создаёт набор Linux-источников для системного мониторинга.
    """

    def __init__(
        self,
        usb_file_path: str = "/media/usb/data.bin",
    ) -> None:
        self._usb_file_path = usb_file_path

    def create_sources(
        self,
    ) -> list[DataSource]:
        return [
            PingSource(),
            CpuUsageSource(),
            CpuTemperatureSource(),
            FanSpeedSource(),
            RamUsageSource(),
            DiskUsageSource(),
            NetworkSpeedSource(),
            LoadAverageSource(),
            UptimeSource(),
            UsbFileSource(
                file_path=self._usb_file_path
            ),
        ]