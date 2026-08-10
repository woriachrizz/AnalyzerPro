from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from core.analyzer import Analyzer
from core.websocket_client import DerivWebSocket

from ui.widgets.statistics_panel import StatisticsPanel
from ui.widgets.frequency_table import FrequencyTable
from ui.widgets.digit_stream import DigitStream


MARKETS = {
    "Volatility 10 Index": "R_10",
    "Volatility 10 1s Index": "R_10_1s",
    "Volatility 25 Index": "R_25",
    "Volatility 25 1s Index": "R_25_1s",
    "Volatility 50 Index": "R_50",
    "Volatility 50 1s Index": "R_50_1s",
    "Volatility 75 Index": "R_75",
    "Volatility 75 1s Index": "R_75_1s",
    "Volatility 100 Index": "R_100",
    "Volatility 100 1s Index": "R_100_1s",
}


class DashboardPage(QWidget):

    def __init__(self, analyzer, client):
        super().__init__()

        self.setWindowTitle("Analyzer Pro Match")
        self.resize(1100, 700)

        self.analyzer = analyzer
        self.client = client

        self.build_ui()
        self.connect_signals()

        self.client.connect_to_server()

    # --------------------------------------------------

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        # ---------------- Header ----------------

        header = QHBoxLayout()

        title = QLabel("Analyzer Pro Match")
        title.setObjectName("title")

        self.status = QLabel("🔴 Disconnected")
        self.status.setObjectName("status_disconnected")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status)

        main_layout.addLayout(header)

        # ---------------- Controls ----------------

        controls = QHBoxLayout()

        controls.addWidget(QLabel("Market"))

        self.market = QComboBox()
        self.market.addItems(MARKETS.keys())
        controls.addWidget(self.market)

        controls.addSpacing(20)

        controls.addWidget(QLabel("Window"))

        self.window = QComboBox()
        self.window.addItems([
            "25",
            "50",
            "100",
            "250",
            "500",
            "1000",
            "Session"
        ])
        self.window.setCurrentText("100")

        controls.addWidget(self.window)
        controls.addStretch()

        main_layout.addLayout(controls)

        # ---------------- Statistics ----------------

        self.statistics = StatisticsPanel()
        main_layout.addWidget(self.statistics)

        # ---------------- Frequency Table ----------------

        self.table = FrequencyTable()
        main_layout.addWidget(self.table)

        # ---------------- Digit Stream ----------------

        self.stream = DigitStream()
        main_layout.addWidget(self.stream)

    # --------------------------------------------------

    def connect_signals(self):

        self.client.connected.connect(self.connected)
        self.client.disconnected.connect(self.disconnected)
        self.client.tick_received.connect(self.update_tick)

        self.market.currentTextChanged.connect(
            self.market_changed
        )

        self.window.currentTextChanged.connect(
            lambda _: self.refresh_table()
        )

    # --------------------------------------------------

    def connected(self):

        self.status.setText("🟢 Connected")
        self.status.setObjectName("status_connected")

    # --------------------------------------------------

    def disconnected(self):

        self.status.setText("🔴 Disconnected")
        self.status.setObjectName("status_disconnected")

    # --------------------------------------------------

    def market_changed(self, text):

        symbol = MARKETS[text]

        self.analyzer.reset()

        self.client.subscribe(symbol)

        self.refresh_table()

    # --------------------------------------------------

    def update_tick(self, quote, digit):

        print("Dashboard:", quote, digit)

        # Update backend

        self.analyzer.process_tick(quote, digit)

        # ---------------- Statistics ----------------

        self.statistics.tick_card.set_value(f"{quote:.3f}")

        self.statistics.digit_card.set_value(str(digit))

        self.statistics.counter_card.set_value(
            str(self.analyzer.get_total_ticks())
        )

        self.statistics.runtime_card.set_value(
            self.analyzer.get_runtime()
        )

        # ---------------- Match Statistics ----------------

        stats = self.analyzer.get_match_stats()

        self.statistics.match_card.set_value(
            f"{stats['match_percent']:.2f}%"
        )

        self.statistics.differ_card.set_value(
            f"{stats['differ_percent']:.2f}%"
        )

        self.statistics.match_streak.set_value(
            str(stats["current_match_streak"])
        )

        self.statistics.differ_streak.set_value(
            str(stats["current_differ_streak"])
        )

        # ---------------- Frequency Table ----------------

        self.refresh_table()

        # ---------------- Digit Stream ----------------

        self.stream.add_digit(digit)

    # --------------------------------------------------

    def refresh_table(self):

        window = self.window.currentText()

        if window.lower() == "session":
            rows = self.analyzer.get_frequency_table("session")
        else:
            rows = self.analyzer.get_frequency_table(
                int(window)
            )

        self.table.update_table(rows)