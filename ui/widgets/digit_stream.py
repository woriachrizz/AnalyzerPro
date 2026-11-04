from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class DigitStream(QWidget):

    def __init__(self, max_digits=30):
        super().__init__()

        self.max_digits = max_digits
        self.digits = deque(maxlen=max_digits)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(6)

        self.labels = []

        for _ in range(max_digits):

            label = QLabel("-")

            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(32, 32)

            label.setStyleSheet("""
                QLabel{
                    background:#2b2b2b;
                    color:white;
                    border-radius:6px;
                    font-size:16px;
                    font-weight:bold;
                }
            """)

            self.layout.addWidget(label)
            self.labels.append(label)

        self.layout.addStretch()

    # --------------------------------------------------

    def add_digit(self, digit):

        self.digits.appendleft(str(digit))

        for i, label in enumerate(self.labels):

            if i < len(self.digits):
                label.setText(self.digits[i])
            else:
                label.setText("-")

    def clear(self):
        self.digits.clear()
        for label in self.labels:
            label.setText("-")
