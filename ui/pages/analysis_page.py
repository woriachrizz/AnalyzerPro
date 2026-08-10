from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class AnalysisPage(QWidget):

    def __init__(self, analyzer):
        super().__init__()

        self.analyzer = analyzer

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Analysis Page\n\nComing Soon...")
        )