import sys

from PySide6.QtWidgets import QApplication

from ui.dashboard import Dashboard
from ui.theme import DARK_THEME


def main():
    app = QApplication(sys.argv)

    # Apply the application theme
    app.setStyleSheet(DARK_THEME)

    # Create and show the main window
    window = Dashboard()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()