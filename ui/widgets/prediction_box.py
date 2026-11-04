from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
)


class PredictionBox(QGroupBox):

    analyze_requested = Signal(str, int)

    def __init__(self):
        super().__init__("Prediction Analysis")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        self.setStyleSheet("""
            QGroupBox {
                background: #2b2d31;
                border: 1px solid #3c4043;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                margin-top: 12px;
                padding: 12px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }

            QLabel {
                color: white;
                font-size: 11pt;
                font-weight: normal;
            }

            QPushButton {
                background: #3c4043;
                color: white;
                border: 1px solid #5f6368;
                border-radius: 6px;
                padding: 7px;
            }

            QPushButton:hover {
                background: #4a4d52;
            }
        """)

        # ---------------- Digit Selection ----------------

        form = QFormLayout()

        self.kind = QComboBox()
        self.kind.addItems([
            "Odd",
            "Even",
            "Match",
            "Differs",
            "Over",
            "Under",
        ])

        self.horizon = QComboBox()
        for tick_count in (1, 5, 10, 25):
            self.horizon.addItem(f"Next {tick_count} tick(s)", tick_count)

        form.addRow(
            "Contract:",
            self.kind
        )

        form.addRow("Forecast horizon:", self.horizon)

        layout.addLayout(form)

        # ---------------- Analyze Button ----------------

        self.analyze_button = QPushButton(
            "Analyze & Track"
        )

        layout.addWidget(
            self.analyze_button
        )

        # ---------------- Results ----------------

        self.result_panel = QWidget()
        self.result_panel.setStyleSheet("""
            QWidget {
                background: #202124;
                border: 1px solid #3c4043;
                border-radius: 6px;
            }
        """)

        result_layout = QVBoxLayout(self.result_panel)
        result_layout.setSpacing(8)

        self.report_title = QLabel(
            "Prediction Report"
        )
        self.report_title.setStyleSheet(
            "color: #8ab4f8; font-size: 12pt; font-weight: bold; border: none;"
        )

        self.digit_label = QLabel("Prediction: --")
        self.frequency_label = QLabel("Chance on next tick: --")
        self.horizon_label = QLabel("Chance within horizon: --")
        self.sample_rate_label = QLabel("Observed sample rate: --")
        self.rank_label = QLabel("Baseline: --")
        self.appearances_label = QLabel("Appearances: --")
        self.gap_label = QLabel("Barrier ties: --")
        self.sample_label = QLabel("Sample: --")
        self.confidence_label = QLabel("Baseline deviation: --")
        self.tracking_label = QLabel("Tracking: Select a contract and start analysis")
        self.status_label = QLabel("Status: No analysis started")
        self.recommendation_label = QLabel(
            "Signal: Waiting for analysis."
        )
        self.recommendation_label.setWordWrap(True)

        for label in (
            self.digit_label,
            self.frequency_label,
            self.horizon_label,
            self.sample_rate_label,
            self.rank_label,
            self.appearances_label,
            self.gap_label,
            self.sample_label,
            self.confidence_label,
            self.tracking_label,
            self.status_label,
            self.recommendation_label,
        ):
            label.setStyleSheet("border: none; color: white;")
            result_layout.addWidget(label)

        result_layout.insertWidget(0, self.report_title)
        layout.addWidget(self.result_panel)

        self.analyze_button.clicked.connect(
            self.request_analysis
        )

    # --------------------------------------------------

    def request_analysis(self):

        kind = self.kind.currentText()
        print(f"🎯 Analyze button clicked — {kind}")

        self.analyze_requested.emit(
            kind,
            int(self.horizon.currentData()),
        )

    # --------------------------------------------------

    def update_result(self, result, show_logs=True):

        if show_logs:
            print("🖥️ Updating PredictionBox:", result)

        self.digit_label.setText(f"Predicted digit: {result.get('predicted_digit', '--')} — {result.get('digit_probability', 0):.2f}% chance next tick ({result.get('description', result.get('kind', '--'))})")

        self.frequency_label.setText(
            f"Chance on next tick: {result.get('frequency', 0):.2f}%"
        )

        self.horizon_label.setText(
            f"Chance at least once in next {result.get('horizon', 1)} ticks: "
            f"{result.get('horizon_probability', 0):.2f}%"
        )

        self.sample_rate_label.setText(
            f"Observed sample rate: {result.get('sample_frequency', 0):.2f}%"
        )

        self.rank_label.setText(
            f"Baseline: {result.get('baseline', '--')}%"
        )

        self.appearances_label.setText(
            f"Appearances: {result.get('appearances', 0)}"
        )

        self.gap_label.setText(
            "Barrier ties: "
            f"{result.get('ties') if result.get('ties') is not None else '--'}"
        )

        self.sample_label.setText(
            f"Sample: {result.get('sample_size', 0)} ticks"
        )

        self.confidence_label.setText(
            f"Baseline deviation: {result.get('baseline_deviation', 0):.2f} percentage points"
        )

        self.tracking_label.setText(
            f"Forward tracking (one result per tick, {result.get('kind', '')}): "
            f"{result.get('prediction_hits', 0)} hits, "
            f"{result.get('prediction_misses', 0)} misses from "
            f"{result.get('prediction_total', 0)} ticks "
            f"({result.get('prediction_hit_percent', 0):.2f}% hits, "
            f"{result.get('prediction_miss_percent', 0):.2f}% misses)"
        )

        self.status_label.setText(
            f"Status: {result.get('status', '--')}"
        )

        self.recommendation_label.setText(
            f"Analysis: {result.get('recommendation', '--')}"
        )

        self.apply_status_style(
            result.get("status", "")
        )

        # Force the widget to repaint
        self.digit_label.repaint()
        self.frequency_label.repaint()
        self.horizon_label.repaint()
        self.sample_rate_label.repaint()
        self.rank_label.repaint()
        self.appearances_label.repaint()
        self.gap_label.repaint()
        self.sample_label.repaint()
        self.confidence_label.repaint()
        self.tracking_label.repaint()
        self.status_label.repaint()
        self.recommendation_label.repaint()

    # --------------------------------------------------

    def apply_status_style(self, status):

        color = "#e8eaed"

        if status == "HIGH FREQUENCY":
            color = "#fbbc04"

        elif status == "LOW FREQUENCY":
            color = "#ff8a80"

        elif status == "MEDIUM":
            color = "#81c995"

        elif status == "NO DATA":
            color = "#9aa0a6"

        elif status == "IMPOSSIBLE":
            color = "#ff8a80"

        self.status_label.setStyleSheet(
            f"border: none; color: {color}; font-weight: bold;"
        )
