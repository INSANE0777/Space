import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from main import run_goal
from notifications import notification_center


@dataclass
class ScheduledGoal:
    task_id: str
    goal: str
    interval_seconds: int
    change_key: Optional[str] = None
    notify_on_change: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    last_hash: Optional[str] = None
    last_payload: Optional[Dict[str, Any]] = None
    last_notification: Optional[datetime] = None

    def schedule_next(self):
        self.last_run = datetime.now(timezone.utc)
        self.next_run = self.last_run + timedelta(seconds=self.interval_seconds)


class GoalScheduler:
    """Lightweight background scheduler for recurring goals."""

    def __init__(self):
        self._tasks: Dict[str, ScheduledGoal] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def add_task(self, task: ScheduledGoal):
        with self._lock:
            if task.task_id in self._tasks:
                raise ValueError(f"Task '{task.task_id}' already exists")
            task.schedule_next()
            self._tasks[task.task_id] = task

    def load_from_file(self, path: str | Path):
        config_path = Path(path)
        if not config_path.exists():
            return
        data = json.loads(config_path.read_text())
        for entry in data.get("tasks", []):
            if not entry.get("enabled", True):
                continue
            task = ScheduledGoal(
                task_id=entry["id"],
                goal=entry["goal"],
                interval_seconds=entry.get("interval_seconds", 3600),
                change_key=entry.get("change_key"),
                notify_on_change=entry.get("notify_on_change", True),
            )
            self.add_task(task)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def list_tasks(self) -> List[Dict[str, Any]]:
        with self._lock:
            tasks = []
            for task in self._tasks.values():
                tasks.append(
                    {
                        "id": task.task_id,
                        "goal": task.goal,
                        "interval_seconds": task.interval_seconds,
                        "change_key": task.change_key,
                        "next_run": task.next_run.isoformat() if task.next_run else None,
                        "last_run": task.last_run.isoformat() if task.last_run else None,
                        "last_notification": task.last_notification.isoformat()
                        if task.last_notification
                        else None,
                    }
                )
            return tasks

    def _run_loop(self):
        notification_center.notify(
            "Scheduler Started",
            "Goal scheduler is now monitoring recurring tasks.",
            level="info",
        )
        while not self._stop_event.is_set():
            now = datetime.now(timezone.utc)
            due_tasks = []
            with self._lock:
                for task in self._tasks.values():
                    if task.next_run and task.next_run <= now:
                        due_tasks.append(task)
            for task in due_tasks:
                self._execute_task(task)
            time.sleep(1)

    def _execute_task(self, task: ScheduledGoal):
        try:
            result = run_goal(task.goal)
            payload = result.get(task.change_key) if task.change_key else result
            payload_hash = self._hash_payload(payload)

            if task.notify_on_change and payload_hash != task.last_hash:
                notification_center.notify(
                    title="Goal Update Detected",
                    message=f"Task '{task.task_id}' detected new data for goal '{task.goal}'.",
                    payload={
                        "task_id": task.task_id,
                        "goal": task.goal,
                        "change_key": task.change_key,
                        "data": payload,
                    },
                    level="success",
                )
                task.last_notification = datetime.now(timezone.utc)
                task.last_payload = payload
                task.last_hash = payload_hash
        except Exception as exc:
            notification_center.notify(
                title="Scheduler Error",
                message=f"Task '{task.task_id}' failed: {exc}",
                payload={"task_id": task.task_id},
                level="error",
            )
        finally:
            with self._lock:
                task.schedule_next()

    @staticmethod
    def _hash_payload(payload: Any) -> Optional[str]:
        if payload is None:
            return None
        try:
            import hashlib
            import json as json_lib

            payload_str = json_lib.dumps(payload, sort_keys=True, default=str)
            return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        except Exception:
            return None


def start_scheduler_from_config(config_path: str = "scheduler_config.json") -> GoalScheduler | None:
    scheduler = GoalScheduler()
    scheduler.load_from_file(config_path)
    if scheduler.list_tasks():
        scheduler.start()
        return scheduler
    return None


if __name__ == "__main__":
    scheduler = start_scheduler_from_config()
    if scheduler:
        print("Scheduler running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
    else:
        print("No scheduled tasks found. Create scheduler_config.json to add tasks.")

