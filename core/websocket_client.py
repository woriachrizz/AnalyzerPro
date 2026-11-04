import json

from PySide6.QtCore import QObject, Signal, QTimer, QUrl
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QAbstractSocket


class DerivWebSocket(QObject):
    """
    Public Deriv market-data WebSocket.

    Handles:
    - Connection
    - Active symbol discovery
    - Tick subscriptions
    - Live tick data
    """

    connected = Signal()
    disconnected = Signal()
    tick_received = Signal(float, int, str)
    error = Signal(str)
    symbols_received = Signal(dict)

    PUBLIC_URL = "wss://api.derivws.com/trading/v1/options/ws/public"

    def __init__(self):
        super().__init__()

        self.ws = QWebSocket()

        self.current_symbol = None
        self.subscription_id = None
        self.connected_once = False
        self.display_precision = 3
        self.reconnect_delay = 1000
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self.connect_to_server)
        self.keepalive_timer = QTimer(self)
        self.keepalive_timer.setInterval(25000)
        self.keepalive_timer.timeout.connect(self.send_keepalive)

        self.ws.connected.connect(self.on_connected)
        self.ws.disconnected.connect(self.on_disconnected)
        self.ws.textMessageReceived.connect(self.on_message)
        self.ws.errorOccurred.connect(self.on_error)

    # --------------------------------------------------
    # CONNECTION
    # --------------------------------------------------

    def connect_to_server(self):

        if self.ws.state() == QAbstractSocket.ConnectedState:
            return

        if self.ws.state() != QAbstractSocket.UnconnectedState:
            self.schedule_reconnect()
            return

        print("Connecting to Deriv public WebSocket...")
        print(f"URL: {self.PUBLIC_URL}")

        self.ws.open(QUrl(self.PUBLIC_URL))

    def set_display_precision(self, precision):
        self.display_precision = int(precision)

    def schedule_reconnect(self):
        if self.reconnect_timer.isActive():
            return
        delay = self.reconnect_delay
        self.reconnect_delay = min(self.reconnect_delay * 2, 30000)
        print(f"Reconnecting to Deriv in {delay / 1000:g}s...")
        self.reconnect_timer.start(delay)

    def send_keepalive(self):
        if self.ws.state() == QAbstractSocket.ConnectedState:
            self.ws.sendTextMessage(json.dumps({"ping": 1}))

    # --------------------------------------------------

    def disconnect(self):

        if self.ws.state() == QAbstractSocket.ConnectedState:
            self.ws.close()

    # --------------------------------------------------
    # CONNECTED
    # --------------------------------------------------

    def on_connected(self):

        print("✅ Connected to Deriv!")

        self.connected_once = True
        self.subscription_id = None
        self.reconnect_delay = 1000
        self.reconnect_timer.stop()
        self.keepalive_timer.start()

        self.connected.emit()

        # Request available symbols
        self.request_active_symbols()
        if self.current_symbol:
            self.subscribe(self.current_symbol)

    # --------------------------------------------------
    # ACTIVE SYMBOLS
    # --------------------------------------------------

    def request_active_symbols(self):

        request = {
            "active_symbols": "brief",
            "req_id": 1
        }

        print("Requesting active symbols...")
        print(json.dumps(request))

        self.ws.sendTextMessage(
            json.dumps(request)
        )

    # --------------------------------------------------
    # SUBSCRIBE
    # --------------------------------------------------

    def subscribe(self, symbol):

        if not symbol:
            print("❌ Cannot subscribe: empty symbol")
            return

        previous_symbol = self.current_symbol
        if (
            previous_symbol
            and previous_symbol != symbol
            and self.subscription_id
            and self.ws.state() == QAbstractSocket.ConnectedState
        ):
            self.ws.sendTextMessage(json.dumps({"forget": self.subscription_id}))

        self.current_symbol = symbol

        if self.ws.state() != QAbstractSocket.ConnectedState:
            return

        request = {
            "ticks": symbol,
            "subscribe": 1,
            "req_id": 2
        }

        print(f"📡 Subscribing to: {symbol}")
        print(json.dumps(request))

        self.ws.sendTextMessage(
            json.dumps(request)
        )

    # --------------------------------------------------
    # DISCONNECTED
    # --------------------------------------------------

    def on_disconnected(self):

        print("❌ Disconnected from Deriv")

        self.disconnected.emit()
        self.keepalive_timer.stop()
        self.schedule_reconnect()

    # --------------------------------------------------
    # ERROR
    # --------------------------------------------------

    def on_error(self, socket_error):

        message = self.ws.errorString()

        print("❌ WebSocket Error:", message)

        self.error.emit(message)
        self.schedule_reconnect()

    # --------------------------------------------------
    # MESSAGE
    # --------------------------------------------------

    def on_message(self, message):

        try:
            data = json.loads(message)

        except json.JSONDecodeError as exc:

            print("❌ JSON error:", exc)

            return

        msg_type = data.get("msg_type")

        # --------------------------------------------------
        # ACTIVE SYMBOLS
        # --------------------------------------------------

        if msg_type == "active_symbols":

            symbols = data.get("active_symbols", [])

            print(
                f"📊 Active symbols received: {len(symbols)}"
            )

            symbol_map = {}

            for item in symbols:

                symbol = item.get(
                    "underlying_symbol"
                )

                name = item.get(
                    "underlying_symbol_name"
                )

                if symbol and name:

                    symbol_map[name] = symbol

                    print(
                        f"   {name} -> {symbol}"
                    )

            self.symbols_received.emit(symbol_map)

            # Automatically subscribe to the default market
            if not self.current_symbol:

                preferred = [
                    "Volatility 25 Index",
                    "Volatility 25 (1s) Index",
                ]

                for name in preferred:

                    if name in symbol_map:

                        self.subscribe(
                            symbol_map[name]
                        )

                        break

            return

        # --------------------------------------------------
        # TICK
        # --------------------------------------------------

        if msg_type == "tick":

            subscription = data.get("subscription") or {}
            self.subscription_id = subscription.get("id", self.subscription_id)

            tick = data.get("tick")

            if not tick:
                print("⚠️ Tick message without tick data")
                return

            quote = tick.get("quote")

            if quote is None:
                print("⚠️ Tick has no quote")
                return

            quote_string = f"{float(quote):.{self.display_precision}f}"
            digit = int(quote_string[-1])

            self.tick_received.emit(
                float(quote),
                digit,
                quote_string
            )

            return

        # --------------------------------------------------
        # ERROR RESPONSE
        # --------------------------------------------------

        if "error" in data:

            error_data = data["error"]

            code = error_data.get(
                "code",
                "Unknown"
            )

            message_text = error_data.get(
                "message",
                "Unknown error"
            )

            print(
                f"❌ Deriv API Error: "
                f"{code} - {message_text}"
            )

            self.error.emit(
                f"{code}: {message_text}"
            )

            return

        # --------------------------------------------------

        print(
            f"ℹ️ Message type: {msg_type}"
        )
