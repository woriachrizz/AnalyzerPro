import sys

from PySide6.QtWidgets import QApplication

from ui.dashboard import Dashboard
from ui.theme import DARK_THEME

app = QApplication(sys.argv)

app.setStyleSheet(DARK_THEME)

window = Dashboard()

window.show()

sys.exit(app.exec())