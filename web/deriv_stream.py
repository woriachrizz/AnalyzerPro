"""Threaded Deriv public WebSocket client for the Streamlit app."""
import json
import queue
import threading
import time
import websocket


URL = "wss://api.derivws.com/trading/v1/options/ws/public"


class DerivStream:
    def __init__(self, precision=3):
        self.precision = int(precision)
        self.events = queue.Queue(maxsize=5000)
        self.stop_event = threading.Event()
        self.thread = None
        self.ws = None
        self.lock = threading.RLock()
        self.symbol = None
        self.subscription_id = None
        self.connected = False

    def publish(self, event):
        try:
            self.events.put_nowait(event)
        except queue.Full:
            try:
                self.events.get_nowait()
                self.events.put_nowait(event)
            except queue.Empty:
                pass

    def start(self, symbol):
        self.set_symbol(symbol)
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def set_symbol(self, symbol):
        if not symbol:
            return
        with self.lock:
            changed = symbol != self.symbol
            old_id = self.subscription_id
            self.symbol = symbol
            if changed:
                self.subscription_id = None
            ws, connected = self.ws, self.connected
        if changed and connected and ws:
            try:
                if old_id:
                    ws.send(json.dumps({"forget": old_id}))
                self.subscribe(ws, symbol)
            except Exception as exc:
                self.publish({"type": "status", "status": "error", "message": str(exc)})

    def set_precision(self, precision):
        self.precision = int(precision)

    def subscribe(self, ws, symbol):
        ws.send(json.dumps({"ticks": symbol, "subscribe": 1, "req_id": 2}))

    def stop(self):
        self.stop_event.set()
        with self.lock:
            ws = self.ws
            self.connected = False
        if ws:
            try:
                ws.close()
            except Exception:
                pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

    def on_open(self, ws):
        with self.lock:
            self.connected = True
            symbol = self.symbol
            self.subscription_id = None
        self.publish({"type": "status", "status": "connected", "message": "Connected to Deriv"})
        ws.send(json.dumps({"active_symbols": "brief", "req_id": 1}))
        if symbol:
            self.subscribe(ws, symbol)

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
        except (TypeError, json.JSONDecodeError):
            return
        if "error" in data:
            err = data["error"]
            self.publish({"type": "status", "status": "error", "message": f'{err.get("code", "Error")}: {err.get("message", "Unknown")}'})
            return
        if data.get("msg_type") == "active_symbols":
            symbols = {}
            for item in data.get("active_symbols", []):
                if item.get("underlying_symbol") and item.get("underlying_symbol_name"):
                    symbols[item["underlying_symbol_name"]] = item["underlying_symbol"]
            self.publish({"type": "symbols", "symbols": symbols})
            return
        if data.get("msg_type") != "tick":
            return
        tick = data.get("tick") or {}
        if tick.get("quote") is None:
            return
        try:
            quote = float(tick["quote"])
            quote_text = f"{quote:.{self.precision}f}"
            digit = int(quote_text[-1])
        except (ValueError, TypeError, IndexError):
            return
        sub = data.get("subscription") or {}
        if sub.get("id"):
            with self.lock:
                self.subscription_id = sub["id"]
        self.publish({
            "type": "tick", "quote": quote, "quote_string": quote_text,
            "digit": digit, "epoch": tick.get("epoch"), "symbol": tick.get("symbol")
        })

    def on_error(self, ws, error):
        self.publish({"type": "status", "status": "error", "message": str(error)})

    def on_close(self, ws, code, reason):
        with self.lock:
            self.connected = False
            self.subscription_id = None
        if not self.stop_event.is_set():
            self.publish({"type": "status", "status": "reconnecting", "message": f"Connection closed: {reason or code}"})

    def run(self):
        delay = 1
        while not self.stop_event.is_set():
            app = websocket.WebSocketApp(
                URL, on_open=self.on_open, on_message=self.on_message,
                on_error=self.on_error, on_close=self.on_close
            )
            with self.lock:
                self.ws = app
            try:
                app.run_forever(ping_interval=25, ping_timeout=10)
            except Exception as exc:
                self.publish({"type": "status", "status": "error", "message": str(exc)})
            if self.stop_event.is_set():
                break
            self.publish({"type": "status", "status": "reconnecting", "message": f"Retrying in {delay}s"})
            self.stop_event.wait(delay)
            delay = min(delay * 2, 30)
