from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame
)


from PySide6.QtCore import Qt, Signal
from core.websocket_client import DerivWebSocket

class Dashboard(QMainWindow):
    tick_received = Signal(float, str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Deriv Analyzer Pro")
        self.resize(1400, 800)

        central = QWidget()
        self.setCentralWidget(central)

        main = QVBoxLayout()

        # Header
        header = QHBoxLayout()

        title = QLabel("DERIV ANALYZER PRO")
        title.setStyleSheet("font-size:28px;font-weight:bold;")

        self.status = QLabel("🟢 Connected")
        self.status.setStyleSheet("color:#00E676;font-size:16px;")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status)

        main.addLayout(header)

        # Market Selection
        market_layout = QHBoxLayout()

        market_layout.addWidget(QLabel("Market"))

        self.market = QComboBox()

        self.market.addItems([
            "Volatility 10",
            "Volatility 25",
            "Volatility 50",
            "Volatility 75",
            "Volatility 100"
        ])

        market_layout.addWidget(self.market)
        market_layout.addStretch()

        main.addLayout(market_layout)

        # Cards
        cards = QHBoxLayout()

        self.tick_card = self.create_card("Current Tick", "----")

        self.digit_card = self.create_card("Last Digit", "-")

        self.total_card = self.create_card("Total Ticks", "0")

        cards.addWidget(self.tick_card)
        cards.addWidget(self.digit_card)
        cards.addWidget(self.total_card)

        main.addLayout(cards)

        central.setLayout(main)
        self.tick_label = self.tick_card.findChildren(QLabel)[1]
        self.digit_label = self.digit_card.findChildren(QLabel)[1]
        self.total_label = self.total_card.findChildren(QLabel)[1]
        self.tick_count = 0
        self.tick_received.connect(self.update_dashboard)
        self.client = DerivWebSocket(self.receive_tick)
        self.client.start("R_25")

    def create_card(self, title, value):

        frame = QFrame()

        layout = QVBoxLayout()

        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)

        v = QLabel(value)
        v.setAlignment(Qt.AlignCenter)
        v.setStyleSheet("""
            font-size:30px;
            font-weight:bold;
            color:#00E676;
        """)

        layout.addWidget(t)
        layout.addWidget(v)

        frame.setLayout(layout)

        return frame
    
    def receive_tick(self, quote, digit):
        self.tick_received.emit(quote, digit)

    def update_dashboard(self, quote, digit):

        self.tick_count += 1
        
        self.tick_label.setText(str(quote))
        self.digit_label.setText(str(digit))
        self.total_label.setText(str(self.tick_count))