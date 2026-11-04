from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.analyzer import Analyzer
from core.websocket_client import DerivWebSocket

from ui.widgets.statistics_panel import StatisticsPanel
from ui.widgets.frequency_table import FrequencyTable
from ui.widgets.digit_stream import DigitStream
from ui.widgets.prediction_box import PredictionBox


MARKETS = {
    "Volatility 10 Index": "R_10",
    "Volatility 10 (1s) Index": "1HZ10V",
    "Volatility 25 Index": "R_25",
    "Volatility 25 (1s) Index": "1HZ25V",
    "Volatility 50 Index": "R_50",
    "Volatility 50 (1s) Index": "1HZ50V",
    "Volatility 75 Index": "R_75",
    "Volatility 75 (1s) Index": "1HZ75V",
    "Volatility 100 Index": "R_100",
    "Volatility 100 (1s) Index": "1HZ100V",
}


class DashboardPage(QWidget):

    def __init__(self, analyzer, client):
        super().__init__()

        self.setWindowTitle("Analyzer Pro Match")
        self.resize(1100, 700)

        self.analyzer = analyzer
        self.client = client
        self.prediction_auto_refresh = False

        self.build_ui()
        self.connect_signals()
        self.client.subscribe(MARKETS[self.market.currentText()])


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
        controls.addSpacing(20)
        controls.addWidget(QLabel("Tick decimals"))
        self.precision = QComboBox()
        self.precision.addItem("2", 2)
        self.precision.addItem("3", 3)
        self.precision.setCurrentIndex(1)
        self.precision.setToolTip(
            "Changing precision starts a fresh sample so digit statistics stay consistent."
        )
        controls.addWidget(self.precision)
        controls.addStretch()

        main_layout.addLayout(controls)

        # ---------------- Main Content ----------------

        content = QHBoxLayout()
        content.setSpacing(15)

        left_panel = QVBoxLayout()

        # ---------------- Statistics ----------------

        self.statistics = StatisticsPanel()
        left_panel.addWidget(self.statistics)

        # ---------------- Frequency Table ----------------

        self.table = FrequencyTable()
        left_panel.addWidget(self.table, 1)

        # ---------------- Digit Stream ----------------

        self.stream = DigitStream()
        left_panel.addWidget(self.stream)

        content.addLayout(left_panel, 1)

        # ---------------- Prediction Box ----------------

        self.prediction_box = PredictionBox()
        self.prediction_box.setMinimumWidth(280)
        self.prediction_box.setMinimumHeight(560)
        self.prediction_box.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Preferred
        )

        self.prediction_scroll = QScrollArea()
        self.prediction_scroll.setWidgetResizable(True)
        self.prediction_scroll.setFrameShape(QFrame.NoFrame)
        self.prediction_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.prediction_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.prediction_scroll.setMinimumWidth(300)
        self.prediction_scroll.setMaximumWidth(380)
        self.prediction_scroll.setWidget(self.prediction_box)

        content.addWidget(self.prediction_scroll)

        main_layout.addLayout(content, 1)

    # --------------------------------------------------

    def connect_signals(self):

        self.client.connected.connect(self.connected)
        self.client.disconnected.connect(self.disconnected)
        self.client.tick_received.connect(self.update_tick)

        self.market.currentTextChanged.connect(
            self.market_changed
        )

        self.window.currentTextChanged.connect(
            self.window_changed
        )
        self.precision.currentIndexChanged.connect(
            self.precision_changed
        )
        self.client.set_display_precision(self.precision.currentData())
        self.prediction_box.analyze_requested.connect(
            self.analyze_prediction
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
        self.prediction_auto_refresh = False
        self.stream.clear()
        self.statistics.tick_card.set_value("--")
        self.statistics.digit_card.set_value("--")
        self.statistics.counter_card.set_value("0")
        self.statistics.runtime_card.set_value("00:00:00")
        self.statistics.match_card.set_value("0.00%")
        self.statistics.differ_card.set_value("0.00%")
        self.statistics.match_streak.set_value("0")
        self.statistics.differ_streak.set_value("0")

        self.client.subscribe(symbol)

        self.refresh_table()
        self.refresh_prediction_report()

    # --------------------------------------------------

    def update_tick(self, quote, digit, quote_string):

        # Update backend

        self.analyzer.process_tick(quote, digit)

        # ---------------- Statistics ----------------

        self.statistics.tick_card.set_value(quote_string)

        self.statistics.digit_card.set_value(str(digit))

        self.statistics.counter_card.set_value(
            str(self.analyzer.get_total_ticks())
        )

        self.statistics.runtime_card.set_value(
            self.analyzer.get_runtime()
        )

        # ---------------- Prediction Tracking ----------------

        stats = self.analyzer.get_prediction_stats()

        self.statistics.match_card.set_value(
            f"{stats['hit_percent']:.2f}%"
        )

        self.statistics.differ_card.set_value(
            f"{stats['miss_percent']:.2f}%"
        )

        self.statistics.match_streak.set_value(
            str(stats["current_hit_streak"])
        )

        self.statistics.differ_streak.set_value(
            str(stats["current_miss_streak"])
        )

        # ---------------- Frequency Table ----------------

        self.refresh_table()

        # ---------------- Digit Stream ----------------

        self.stream.add_digit(digit)

        if self.analyzer.prediction_kind is not None:
            self.prediction_auto_refresh = True
            self.refresh_prediction_report(
                show_logs=False
            )

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

    # --------------------------------------------------

    def window_changed(self):

        self.refresh_table()

        if self.prediction_auto_refresh:
            self.refresh_prediction_report(
                show_logs=False
            )

    # --------------------------------------------------

    def precision_changed(self):
        precision = self.precision.currentData()
        if precision == self.client.display_precision:
            return

        self.client.set_display_precision(precision)
        self.analyzer.reset()
        self.prediction_auto_refresh = False
        self.stream.clear()
        self.statistics.tick_card.set_value("--")
        self.statistics.digit_card.set_value("--")
        self.statistics.counter_card.set_value("0")
        self.statistics.runtime_card.set_value("00:00:00")
        self.statistics.match_card.set_value("0.00%")
        self.statistics.differ_card.set_value("0.00%")
        self.statistics.match_streak.set_value("0")
        self.statistics.differ_streak.set_value("0")
        self.refresh_table()
        self.refresh_prediction_report()

    # --------------------------------------------------

    def analyze_prediction(self, kind, horizon):

        print(f"🔎 Forecasting {kind} over {horizon} tick(s)")

        self.prediction_auto_refresh = True
        self.refresh_prediction_report(kind, None, horizon, show_logs=True, start_tracking=True)

    # --------------------------------------------------

    def refresh_prediction_report(self, kind=None, target=None, horizon=None, show_logs=False, start_tracking=False):

        if kind is None:
            if self.prediction_auto_refresh and self.analyzer.prediction_kind:
                kind = self.analyzer.prediction_kind
                target = self.analyzer.prediction_target
                horizon = self.analyzer.prediction_horizon
            else:
                kind = self.prediction_box.kind.currentText()
        if horizon is None:
            horizon = int(self.prediction_box.horizon.currentData())

        window = self.window.currentText()

        if show_logs:
            print(f"📊 Analysis window: {window}")

        if window.lower() == "session":
            analysis_window = "session"
        else:
            analysis_window = int(window)

        result = self.analyzer.analyze_prediction(
            kind,
            target,
            analysis_window,
            horizon,
        )
        if start_tracking:
            target = result["target"]
            self.analyzer.set_prediction_target(kind, target, horizon)

        if show_logs:
            print(f"📈 Prediction result: {result}")

        self.prediction_box.update_result(
            result,
            show_logs=show_logs
        )
