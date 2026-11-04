"""Threaded, per-browser-session Deriv public tick client."""
from __future__ import annotations

import json
import queue
import threading
from typing import Any

import websocket


class DerivStream:
    URL = "wss://api.derivws.com/trading/v1/options/ws/public"

    def __init__(self, app_id: str = "1089", symbol: str = "R_25"):
        self.url = f"{self.URL}?app_id={app_id}"
        self.symbol = symbol
        self.events: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=5000)
        self._lock = threading.RLock()
        self._app: websocket.WebSocketApp | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._subscription_id: str | None = None

    def _emit(self, event: dict[str, Any]) -> None:
        try:
            self.events.put_nowait(event)
        except queue.Full:
            try:
                self.events.get_nowait()
                self.events.put_nowait(event)
            except queue.Empty:
                pass

    def _on_open(self, ws) -> None:
        with self._lock:
            symbol = self.symbol
            self._subscription_id = None
        self._emit({"type": "status", "value": "Connected"})
        ws.send(json.dumps({"ticks": symbol, "subscribe": 1, "req_id": 2}))

    def _on_message(self, ws, message: str) -> None:
        try:
            data = json.loads(message)
        except (TypeError, json.JSONDecodeError):
            return

        if data.get("error"):
            error = data["error"]
            self._emit({"type": "error", "value": f'{error.get("code", "API error")}: {error.get("message", "Unknown error")}'})
            return

        if data.get("msg_type") == "tick":
            tick = data.get("tick") or {}
            quote = tick.get("quote")
            if quote is None:
                return
            subscription = data.get("subscription") or {}
            with self._lock:
                self._subscription_id = subscription.get("id", self._subscription_id)
                symbol = self.symbol
            pip_size = tick.get("pip_size")
            precision = int(pip_size) if pip_size is not None else 3
            precision = max(0, min(precision, 10))
            quote_text = f"{float(quote):.{precision}f}"
            try:
                digit = int(quote_text[-1])
            except (ValueError, IndexError):
                return
            self._emit({
                "type": "tick", "symbol": symbol, "quote": float(quote),
                "quote_text": quote_text, "digit": digit,
                "epoch": tick.get("epoch"), "pip_size": precision,
            })

    def _on_error(self, ws, error) -> None:
        self._emit({"type": "error", "value": str(error)})

    def _on_close(self, ws, status_code, message) -> None:
        self._emit({"type": "status", "value": "Disconnected"})

    def _run(self) -> None:
        while self._running:
            self._app = websocket.WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            try:
                self._app.run_forever(ping_interval=25, ping_timeout=10)
            except Exception as exc:
                self._emit({"type": "error", "value": str(exc)})
            if self._running:
                self._emit({"type": "status", "value": "Reconnecting"})
                threading.Event().wait(2)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, name="deriv-stream", daemon=True)
        self._thread.start()

    def set_symbol(self, symbol: str) -> None:
        if symbol == self.symbol:
            return
        with self._lock:
            old_subscription = self._subscription_id
            self.symbol = symbol
            self._subscription_id = None
            app = self._app
        if app and app.sock and app.sock.connected:
            try:
                if old_subscription:
                    app.send(json.dumps({"forget": old_subscription}))
                app.send(json.dumps({"ticks": symbol, "subscribe": 1, "req_id": 2}))
            except Exception as exc:
                self._emit({"type": "error", "value": f"Symbol switch: {exc}"})

    def stop(self) -> None:
        self._running = False
        app = self._app
        if app:
            try:
                app.close()
            except Exception:
                pass
        thread = self._thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=2)
        self._emit({"type": "status", "value": "Stopped"})
