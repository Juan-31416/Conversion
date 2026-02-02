from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from image_scrubber_desktop.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Image Scrubber Desktop")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()