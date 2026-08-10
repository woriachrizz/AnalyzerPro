from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class InfoCard(QFrame):
    def __init__(self, title: str, value: str = "--"):
        super().__init__()

        self.setObjectName("infoCard")
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)

        self.title = QLabel(title)
        self.title.setObjectName("cardTitle")

        self.value = QLabel(value)
        self.value.setObjectName("cardValue")

        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.value.setFont(font)
        self.value.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.value)

    def set_value(self, value):
        self.value.setText(str(value))