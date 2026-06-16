from __future__ import annotations

import json
from typing import Optional

from core.models import Priority, Task, TaskStatus
from core.task_store import get_store


def create_task(
    title: str,
    description: str,
    priority: str,
    category: str,
    tags: list[str],
    estimated_effort: str,
    deadline_hint: Optional[str] = None,
    assignee: Optional[str] = None,
) -> str:
    task = Task(
        title=title,
        description=description,
        priority=Priority(priority),
        status=TaskStatus.TRIAGED,
        category=category,
        tags=tags,
        estimated_effort=estimated_effort,
        assignee=assignee,
    )
    get_store().create_task(task)
    return json.dumps(task.model_dump(mode="json"), indent=2)


def get_task(task_id: str) -> str:
    task = get_store().get_task(task_id)
    if not task:
        return json.dumps({"error": f"Task {task_id} not found"})
    return json.dumps(task.model_dump(mode="json"), indent=2)


def update_task(task_id: str, **kwargs: object) -> str:
    task = get_store().update_task(task_id, **kwargs)
    if not task:
        return json.dumps({"error": f"Task {task_id} not found"})
    return json.dumps(task.model_dump(mode="json"), indent=2)


def query_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    tasks = get_store().query_tasks(
        status=status,
        priority=priority,
        assignee=assignee,
        date_from=date_from,
        date_to=date_to,
    )
    return json.dumps([t.model_dump(mode="json") for t in tasks], indent=2)


def get_pending_tasks() -> str:
    tasks = get_store().query_tasks(status=TaskStatus.PENDING_TRIAGE.value)
    return json.dumps([t.model_dump(mode="json") for t in tasks], indent=2)


def assign_task(task_id: str, assignee: str, deadline: str) -> str:
    task = get_store().update_task(
        task_id,
        assignee=assignee,
        deadline=deadline,
        status=TaskStatus.SCHEDULED.value,
    )
    if not task:
        return json.dumps({"error": f"Task {task_id} not found"})
    return json.dumps({"success": True, "task": task.model_dump(mode="json")}, indent=2)
