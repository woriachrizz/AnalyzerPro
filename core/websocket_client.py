import json

from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QAbstractSocket


class DerivWebSocket(QObject):
    """
    Handles the connection to the Deriv WebSocket API.
    Emits signals whenever a new tick is received.
    """

    connected = Signal()
    disconnected = Signal()
    tick_received = Signal(float, int)
    error = Signal(str)

    def __init__(self):
        super().__init__()

        self.ws = QWebSocket()

        self.current_symbol = "R_25"

        self.ws.connected.connect(self.on_connected)
        self.ws.disconnected.connect(self.on_disconnected)
        self.ws.textMessageReceived.connect(self.on_message)
        self.ws.errorOccurred.connect(self.on_error)

    # --------------------------------------------------

    def connect_to_server(self):
        print("Connecting to Deriv...")

        self.ws.open(
            QUrl("wss://ws.derivws.com/websockets/v3?app_id=1089")
        )

    # --------------------------------------------------

    def disconnect(self):

        self.ws.close()

    # --------------------------------------------------

    def subscribe(self, symbol):

        self.current_symbol = symbol

        request = {
            "ticks": symbol,
            "subscribe": 1
        }

        self.ws.sendTextMessage(json.dumps(request))

    # --------------------------------------------------

    def on_connected(self):

        print("✅ Connected!")

        self.connected.emit()

        self.subscribe(self.current_symbol)

    # --------------------------------------------------

    def on_disconnected(self):

        print("❌ Disconnected")

        self.disconnected.emit()

    # --------------------------------------------------

    def on_error(self, socket_error):

        print("WebSocket Error:", socket_error)

        self.error.emit(str(error))

    # --------------------------------------------------

    def on_message(self, message):
    
     data = json.loads(message)
    
     if "tick" not in data:
        return

     tick = data["tick"]

     quote = tick["quote"]
     pip_size = tick["pip_size"]

     quote_str = f"{quote:.{pip_size}f}"
     digit = int(quote_str[-1])

     self.tick_received.emit(
        float(quote),
        digit
     )