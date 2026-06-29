import json
import threading
import websocket


class DerivWebSocket:

    def __init__(self, on_tick_callback):
        self.ws = None
        self.on_tick_callback = on_tick_callback

    def start(self, symbol="R_25"):
        thread = threading.Thread(
            target=self._connect,
            args=(symbol,),
            daemon=True
        )
        thread.start()

    def _connect(self, symbol):

        def on_open(ws):
            print("Connected to Deriv")

            ws.send(json.dumps({
                "ticks": symbol,
                "subscribe": 1
            }))

        def on_message(ws, message):

            data = json.loads(message)

            if "tick" in data:

                quote = data["tick"]["quote"]

                last_digit = str(quote)[-1]

                self.on_tick_callback(
                    quote,
                    last_digit
                )

        def on_error(ws, error):
            print("Error:", error)

        def on_close(ws, close_status_code, close_msg):
            print("Disconnected")

        self.ws = websocket.WebSocketApp(
            "wss://ws.derivws.com/websockets/v3?app_id=1089",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        self.ws.run_forever()