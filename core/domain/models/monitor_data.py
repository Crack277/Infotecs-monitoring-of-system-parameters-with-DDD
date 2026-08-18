from dataclasses import dataclass
from datetime import datetime

from core.domain.common.enum import SourceStatus
from core.domain.value_objects.source_id import SourceId


@dataclass(frozen=True, slots=True)
class MonitorData:
    """
    Результат чтения источника мониторинга.
    """

    source_id: SourceId
    value: str
    status: SourceStatus
    timestamp: datetime
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.status is SourceStatus.OK

    @property
    def is_error(self) -> bool:
        return self.status is SourceStatus.ERROR