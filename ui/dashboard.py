from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
)

from core.analyzer import Analyzer
from core.websocket_client import DerivWebSocket

from ui.pages.dashboard_page import DashboardPage
from ui.pages.analysis_page import AnalysisPage
from ui.pages.inspector_page import InspectorPage
from ui.pages.signals_page import SignalsPage
from ui.pages.history_page import HistoryPage
from ui.pages.settings_page import SettingsPage


class Dashboard(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Analyzer Pro Match")
        self.resize(1400, 850)

        # Shared backend
        self.analyzer = Analyzer()
        self.client = DerivWebSocket()

        # Create pages
        self.dashboard_page = DashboardPage(
            self.analyzer,
            self.client
        )

        self.analysis_page = AnalysisPage(
            self.analyzer
        )

        self.inspector_page = InspectorPage(
            self.analyzer
        )

        self.signals_page = SignalsPage(
            self.analyzer
        )

        self.history_page = HistoryPage(
            self.analyzer
        )

        self.settings_page = SettingsPage()

        # Tabs
        tabs = QTabWidget()

        tabs.addTab(
            self.dashboard_page,
            "Dashboard"
        )

        tabs.addTab(
            self.analysis_page,
            "Analysis"
        )

        tabs.addTab(
            self.inspector_page,
            "Inspector"
        )

        tabs.addTab(
            self.signals_page,
            "Signals"
        )

        tabs.addTab(
            self.history_page,
            "History"
        )

        tabs.addTab(
            self.settings_page,
            "Settings"
        )

        self.setCentralWidget(tabs)

        # Start websocket once
        self.client.connect_to_server()