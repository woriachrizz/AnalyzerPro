from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout
)


class InfoCard(QFrame):
    """
    Reusable dashboard card.

    Example:

    -------------------------
    Current Tick

    4567.1238
    -------------------------
    """

    def __init__(self, title, value="0"):
        super().__init__()

        self.setObjectName("card")
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
            color:#B0BEC5;
        """)

        self.value = QLabel(str(value))
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setObjectName("value")

        layout.addWidget(self.title)
        layout.addSpacing(8)
        layout.addWidget(self.value)

    def set_value(self, value):
        """Update the displayed value."""
        self.value.setText(str(value))

    def get_value(self):
        """Return the current displayed value."""
        return self.value.text()