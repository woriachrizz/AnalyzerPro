from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from ui.pages.dashboard_page import MARKETS


class AnalysisPage(QWidget):

    def __init__(self, analyzer, client, dashboard_market):
        super().__init__()
        self.setStyleSheet("""
            QWidget { background-color: #202124; color: #e8eaed; }
            QGroupBox { background-color: #292b30; border: 1px solid #454950; border-radius: 8px; margin-top: 12px; padding: 12px; color: #e8eaed; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #8ab4f8; }
            QComboBox { background-color: #34373d; color: #f1f3f4; border: 1px solid #5f6368; border-radius: 5px; padding: 6px; }
            QComboBox QAbstractItemView { background-color: #292b30; color: #f1f3f4; selection-background-color: #3c5a82; }
            QPushButton { background-color: #315b8a; color: white; border: 1px solid #4778ac; border-radius: 6px; padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #3d6fa5; }
            QScrollArea, QScrollArea > QWidget > QWidget { background-color: #202124; border: none; }
            QScrollBar:vertical { background: #292b30; width: 12px; margin: 0; }
            QScrollBar::handle:vertical { background: #62666d; min-height: 25px; border-radius: 5px; }
        """)

        self.analyzer = analyzer
        self.client = client
        self.dashboard_market = dashboard_market
        self.analysis_active = False
        self.active_target = None

        page_layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        page_layout.addWidget(self.scroll)

        title = QLabel("Market Analysis")
        title.setObjectName("title")
        subtitle = QLabel(
            "Choose a Deriv market and contract type to estimate the next digit outcome."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        controls = QGroupBox("Analysis setup")
        form = QFormLayout(controls)

        self.market = QComboBox()
        self.market.addItems(MARKETS.keys())
        self.market.setCurrentText(self.dashboard_market.currentText())

        self.kind = QComboBox()
        self.kind.addItems(["Odd", "Even", "Match", "Differs", "Over", "Under"])

        self.window = QComboBox()
        self.window.addItems(["25", "50", "100", "250", "500", "1000", "Session"])
        self.window.setCurrentText("100")

        self.horizon = QComboBox()
        for tick_count in (1, 5, 10, 25):
            self.horizon.addItem(f"Next {tick_count} tick(s)", tick_count)

        form.addRow("Market:", self.market)
        form.addRow("Analysis:", self.kind)
        form.addRow("History window:", self.window)
        form.addRow("Forecast horizon:", self.horizon)

        self.run_button = QPushButton("Analyze selected market")
        self.run_button.setMinimumHeight(40)

        setup_layout = QVBoxLayout()
        setup_layout.addWidget(controls)
        setup_layout.addWidget(self.run_button)
        setup = QWidget()
        setup.setLayout(setup_layout)
        setup.setMaximumWidth(520)
        layout.addWidget(setup)

        self.results = QGroupBox("Forecast result")
        results_layout = QVBoxLayout(self.results)
        results_layout.setSpacing(10)

        self.outcome_label = QLabel("Choose the settings, then run an analysis.")
        self.outcome_label.setWordWrap(True)
        self.outcome_label.setStyleSheet("font-size: 14pt; font-weight: bold;")

        self.next_tick_label = QLabel("Next tick probability: --")
        self.horizon_label = QLabel("Chance at least once in horizon: --")
        self.sample_label = QLabel("History and transition context: --")
        self.observed_label = QLabel("Observed sample rate: --")
        self.tracking_label = QLabel("Forward tracking: --")
        self.explanation_label = QLabel(
            "The forecast uses recent digit-to-digit transitions, conditioned on the current last digit."
        )
        self.explanation_label.setWordWrap(True)

        for label in (
            self.outcome_label,
            self.next_tick_label,
            self.horizon_label,
            self.sample_label,
            self.observed_label,
            self.tracking_label,
            self.explanation_label,
        ):
            results_layout.addWidget(label)

        self.results.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(self.results)
        layout.addStretch(1)
        self.scroll.setWidget(content)

        self.kind.currentTextChanged.connect(self.settings_changed)
        self.window.currentTextChanged.connect(self.settings_changed)
        self.horizon.currentIndexChanged.connect(self.settings_changed)
        self.market.currentTextChanged.connect(self.select_market)
        self.dashboard_market.currentTextChanged.connect(self.sync_market)
        self.run_button.clicked.connect(self.run_analysis)
        self.client.tick_received.connect(self.on_tick)

    def select_market(self, market_name):
        self.analysis_active = False
        if self.dashboard_market.currentText() != market_name:
            self.dashboard_market.setCurrentText(market_name)
        self.show_waiting_state()

    def sync_market(self, market_name):
        if self.market.currentText() != market_name:
            self.market.setCurrentText(market_name)

    def show_waiting_state(self, message="Market changed. Run the analysis when ticks arrive."):
        self.outcome_label.setText(message)
        self.next_tick_label.setText("Next tick probability: --")
        self.horizon_label.setText("Chance at least once in horizon: --")
        self.sample_label.setText("History and transition context: --")
        self.observed_label.setText("Observed sample rate: --")
        self.tracking_label.setText("Forward tracking: --")

    def settings_changed(self, *_args):
        if self.analysis_active:
            self.analysis_active = False
            self.analyzer.reset_prediction_tracking()
            self.show_waiting_state("Settings changed. Run the analysis again to update the forecast.")

    def run_analysis(self):
        kind = self.kind.currentText()
        horizon = int(self.horizon.currentData())
        result = self.analyzer.analyze_prediction(kind, window=self._window(), horizon=horizon)
        self.analyzer.set_prediction_target(kind, result["target"], horizon)
        self.active_target = result["target"]
        self.analysis_active = True
        self.refresh_result()

    def on_tick(self, _quote, _digit, _quote_string):
        if self.analysis_active:
            self.refresh_result()

    def refresh_result(self):
        kind = self.kind.currentText()
        horizon = int(self.horizon.currentData())
        result = self.analyzer.analyze_prediction(kind, self.active_target, self._window(), horizon)
        current_digit = result["current_digit"]
        current_text = "not available yet" if current_digit is None else str(current_digit)

        self.outcome_label.setText(
            f"Predicted digit {result['predicted_digit']} ({result['digit_probability']:.2f}% next-tick chance) — {result['description']} on {self.market.currentText()}"
        )
        self.next_tick_label.setText(
            f"Next tick probability, given current digit {current_text}: "
            f"{result['frequency']:.2f}%"
        )
        self.horizon_label.setText(
            f"Chance at least once in the next {horizon} ticks: "
            f"{result['horizon_probability']:.2f}%"
        )
        self.sample_label.setText(
            f"History: {result['sample_size']} ticks; "
            f"{result['transition_contexts']} prior transitions from digit {current_text}"
        )
        self.observed_label.setText(
            f"Observed sample rate for this outcome: {result['sample_frequency']:.2f}%"
        )
        self.tracking_label.setText(
            f"Forward tracking since analysis: {result['prediction_hits']} hits, "
            f"{result['prediction_misses']} misses in {result['prediction_total']} ticks "
            f"({result['prediction_hit_percent']:.2f}% hit rate)"
        )
        if result["status"] == "NO DATA":
            self.explanation_label.setText(
                "No market ticks are available yet. The displayed probability is only the neutral baseline."
            )
        else:
            self.explanation_label.setText(
                f"{result['recommendation']} Forecast horizon uses the transition model; it is an estimate, not a guarantee."
            )

    def _window(self):
        window_text = self.window.currentText()
        return "session" if window_text.lower() == "session" else int(window_text)
