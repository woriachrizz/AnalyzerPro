from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class SignalsPage(QWidget):

    def __init__(self, analyzer):
        super().__init__()

        self.analyzer = analyzer

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Signals Page\n\nComing Soon...")
        )