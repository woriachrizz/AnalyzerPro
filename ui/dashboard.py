from ui.frequency_table import FrequencyTable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from core.analyzer import Analyzer
from core.websocket_client import DerivWebSocket
from ui.cards import InfoCard


MARKETS = {
    "Volatility 10 Index": "R_10",
    "Volatility 25 Index": "R_25",
    "Volatility 50 Index": "R_50",
    "Volatility 75 Index": "R_75",
    "Volatility 100 Index": "R_100",
}


class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Analyzer Pro Match")
        self.resize(1100, 700)

        self.analyzer = Analyzer()
        self.client = DerivWebSocket()

        self.build_ui()
        self.connect_signals()

        self.client.connect_to_server()

    # --------------------------------------------------

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

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

        for market in MARKETS.keys():
            self.market.addItem(market)

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

        # ---------------- Cards ----------------

        cards = QGridLayout()

        self.tick_card = InfoCard("Current Tick", "0")
        self.digit_card = InfoCard("Last Digit", "-")
        self.counter_card = InfoCard("Tick Count", "0")

        cards.addWidget(self.tick_card, 0, 0)
        cards.addWidget(self.digit_card, 0, 1)
        cards.addWidget(self.counter_card, 0, 2)

        main_layout.addLayout(cards)

        # ---------------- Frequency Table ----------------

        self.table = FrequencyTable()

        main_layout.addWidget(self.table)

        # ---------------- Last Digits ----------------

        self.last_digits = QLabel("Last Digits: ")
        self.last_digits.setWordWrap(True)

        main_layout.addWidget(self.last_digits)

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

        self.client.subscribe(symbol)

    # --------------------------------------------------

    def update_tick(self, quote, digit):
        
        self.analyzer.process_tick(quote, digit)
        
        self.tick_card.set_value(f"{quote:.4f}")
        self.digit_card.set_value(str(digit))
        self.counter_card.set_value(
            str(self.analyzer.get_total_ticks())
        )
        
        window = self.window.currentText()
        
        if window.lower() == "session":
            rows = self.analyzer.get_frequency_table("session")
        else:
            rows = self.analyzer.get_frequency_table(int(window))
            
        self.table.update_table(rows)
        
        history = self.analyzer.get_last_digits()
        
        self.last_digits.setText(
            "Last Digits: " + " ".join(str(x) for x in history)
        )

    # --------------------------------------------------

    def refresh_table(self):
        
        window = self.window.currentText()
        
        if window.lower() == "session":
            rows = self.analyzer.get_frequency_table("session")
        else:
            rows = self.analyzer.get_frequency_table(int(window))

        self.table.update_table(rows)