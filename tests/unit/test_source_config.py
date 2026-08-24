import pytest

from core.domain.value_objects.source_config import SourceConfig


def test_source_config_creates_successfully():
    config = SourceConfig(
        name="CPU Usage",
        interval=1.0,
    )

    assert config.name == "CPU Usage"
    assert config.interval == 1.0


@pytest.mark.parametrize(
    "interval",
    [
        0,
        -1,
    ],
)
def test_source_config_interval_must_be_positive(
    interval: float,
):
    with pytest.raises(ValueError):
        SourceConfig(
            name="CPU Usage",
            interval=interval,
        )