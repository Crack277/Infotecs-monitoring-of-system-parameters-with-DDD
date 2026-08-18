from dataclasses import dataclass

from core.domain.common.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class SourceId(ValueObject):
    """
    Уникальный идентификатор источника данных.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError(
                "Source ID не может быть пустым"
            )