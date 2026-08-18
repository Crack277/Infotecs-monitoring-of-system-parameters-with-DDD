from dataclasses import dataclass

from core.domain.common.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class SourceConfig(ValueObject):
    """
    Конфигурация источника мониторинга.

    name:
        Название источника для отображения.

    interval:
        Интервал опроса источника в секундах.
    """

    name: str
    interval: float

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "Source name не может быть пустым"
            )

        if self.interval <= 0:
            raise ValueError(
                "Source interval должен быть > 0"
            )