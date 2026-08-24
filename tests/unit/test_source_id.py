import pytest

from core.domain.value_objects.source_id import SourceId


def test_source_id_creates_successfully():
    source_id = SourceId("cpu")

    assert source_id.value == "cpu"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
    ],
)
def test_source_id_cannot_be_empty(value: str):
    with pytest.raises(ValueError):
        SourceId(value)