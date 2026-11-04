from PySide6.QtWidgets import QWidget, QGridLayout

from ui.widgets.cards import InfoCard


class StatisticsPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QGridLayout(self)

        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(15)

        # ---------- Row 1 ----------

        self.tick_card = InfoCard("Current Tick", "--")
        self.digit_card = InfoCard("Last Digit", "--")
        self.counter_card = InfoCard("Tick Count", "0")
        self.runtime_card = InfoCard("Runtime", "00:00:00")

        layout.addWidget(self.tick_card, 0, 0)
        layout.addWidget(self.digit_card, 0, 1)
        layout.addWidget(self.counter_card, 0, 2)
        layout.addWidget(self.runtime_card, 0, 3)

        # ---------- Row 2 ----------

        self.match_card = InfoCard("Prediction Hit %", "0.00")
        self.differ_card = InfoCard("Prediction Miss %", "0.00")
        self.match_streak = InfoCard("Hit Streak", "0")
        self.differ_streak = InfoCard("Miss Streak", "0")

        layout.addWidget(self.match_card, 1, 0)
        layout.addWidget(self.differ_card, 1, 1)
        layout.addWidget(self.match_streak, 1, 2)
        layout.addWidget(self.differ_streak, 1, 3)
