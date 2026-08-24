from datetime import datetime

from core.domain.common.enum import SourceStatus
from core.domain.models.monitor_data import MonitorData
from core.domain.value_objects.source_id import SourceId


def test_monitor_data_success():
    data = MonitorData(
        source_id=SourceId("cpu"),
        value="25.5%",
        status=SourceStatus.OK,
        timestamp=datetime.now(),
    )

    assert data.is_success is True
    assert data.is_error is False


def test_monitor_data_error():
    data = MonitorData(
        source_id=SourceId("cpu"),
        value="Недоступно",
        status=SourceStatus.ERROR,
        timestamp=datetime.now(),
        error="Source error",
    )

    assert data.is_success is False
    assert data.is_error is True