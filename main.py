import logging
import sys

from PySide6.QtWidgets import QApplication

from core.infra.linux.source_factory import (
    LinuxSourceFactory,
)
from core.presentation.qt.main_window import (
    MainWindow,
)


def configure_logging() -> None:
    """
    Настроить логирование приложения.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
    )


def main() -> int:
    """
    Точка входа приложения.
    """

    configure_logging()

    app = QApplication(
        sys.argv
    )

    source_factory = (
        LinuxSourceFactory()
    )

    window = MainWindow(
        source_factory=source_factory
    )

    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(
        main()
    )