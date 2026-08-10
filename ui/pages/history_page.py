from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class HistoryPage(QWidget):

    def __init__(self, analyzer):
        super().__init__()

        self.analyzer = analyzer

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("History Page\n\nComing Soon...")
        )