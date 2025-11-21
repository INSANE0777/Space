from collections import deque
from datetime import datetime, timezone
from threading import Lock


class NotificationCenter:
    """Thread-safe notification buffer for system-wide alerts."""

    def __init__(self, max_items: int = 100):
        self._events = deque(maxlen=max_items)
        self._lock = Lock()

    def notify(self, title: str, message: str, *, level: str = "info", payload: dict | None = None):
        event = {
            "id": f"evt_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            "title": title,
            "message": message,
            "level": level,
            "payload": payload or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._events.appendleft(event)
        return event

    def list_events(self):
        with self._lock:
            return list(self._events)

    def clear(self):
        with self._lock:
            self._events.clear()


notification_center = NotificationCenter()

