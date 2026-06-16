from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Optional

from core import config
from core.models import Escalation, Priority, Task, TaskStatus


class TaskStore:
    def __init__(self, db_path: str = "smartops.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT,
                    status TEXT NOT NULL DEFAULT 'pending_triage',
                    category TEXT,
                    tags TEXT DEFAULT '[]',
                    estimated_effort TEXT,
                    deadline TEXT,
                    assignee TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    escalation_notes TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS escalations (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    notified INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        data = dict(row)
        data["tags"] = json.loads(data.get("tags") or "[]")
        return Task(**data)

    def create_task(self, task: Task) -> Task:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, title, description, priority, status, category,
                    tags, estimated_effort, deadline, assignee,
                    created_at, updated_at, escalation_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.title,
                    task.description,
                    task.priority.value if task.priority else None,
                    task.status.value,
                    task.category,
                    json.dumps(task.tags),
                    task.estimated_effort,
                    task.deadline.isoformat() if task.deadline else None,
                    task.assignee,
                    task.created_at.isoformat(),
                    task.updated_at.isoformat(),
                    task.escalation_notes,
                ),
            )
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._row_to_task(row) if row else None

    def update_task(self, task_id: str, **kwargs: object) -> Optional[Task]:
        kwargs["updated_at"] = datetime.utcnow().isoformat()
        if "tags" in kwargs and isinstance(kwargs["tags"], list):
            kwargs["tags"] = json.dumps(kwargs["tags"])
        if "deadline" in kwargs and isinstance(kwargs["deadline"], datetime):
            kwargs["deadline"] = kwargs["deadline"].isoformat()
        if "priority" in kwargs and isinstance(kwargs["priority"], Priority):
            kwargs["priority"] = kwargs["priority"].value
        if "status" in kwargs and isinstance(kwargs["status"], TaskStatus):
            kwargs["status"] = kwargs["status"].value

        cols = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [task_id]
        with self._conn() as conn:
            conn.execute(f"UPDATE tasks SET {cols} WHERE id = ?", vals)
        return self.get_task(task_id)

    def query_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[Task]:
        query = "SELECT * FROM tasks WHERE 1=1"
        params: list[object] = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if assignee:
            query += " AND assignee = ?"
            params.append(assignee)
        if date_from:
            query += " AND created_at >= ?"
            params.append(date_from)
        if date_to:
            query += " AND created_at <= ?"
            params.append(date_to)
        query += " ORDER BY created_at DESC"

        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_task(row) for row in rows]

    def create_escalation(self, escalation: Escalation) -> Escalation:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO escalations (id, task_id, reason, created_at, notified)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    escalation.id,
                    escalation.task_id,
                    escalation.reason,
                    escalation.created_at.isoformat(),
                    int(escalation.notified),
                ),
            )
        return escalation

    def get_escalations(self, task_id: Optional[str] = None) -> list[Escalation]:
        query = "SELECT * FROM escalations"
        params: list[object] = []
        if task_id:
            query += " WHERE task_id = ?"
            params.append(task_id)
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            Escalation(
                id=row["id"],
                task_id=row["task_id"],
                reason=row["reason"],
                created_at=datetime.fromisoformat(row["created_at"]),
                notified=bool(row["notified"]),
            )
            for row in rows
        ]


_store: Optional[TaskStore] = None


def get_store() -> TaskStore:
    global _store
    if _store is None:
        _store = TaskStore(config.DATABASE_PATH)
    return _store
