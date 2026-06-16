from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from core.models import TaskStatus
from core.task_store import get_store


def search_similar_tasks(query: str) -> str:
    all_tasks = get_store().query_tasks()
    q = query.lower()
    matches = [
        t
        for t in all_tasks
        if q in t.title.lower()
        or q in t.description.lower()
        or any(q in tag for tag in t.tags)
    ][:5]
    return json.dumps([t.model_dump(mode="json") for t in matches], indent=2)


def get_team_capacity() -> str:
    team: list[dict[str, Any]] = [
        {"name": "Alice Chen",   "role": "Backend Engineer",   "capacity": 5},
        {"name": "Bob Martinez", "role": "Frontend Engineer",  "capacity": 5},
        {"name": "Carol Kim",    "role": "DevOps Engineer",    "capacity": 4},
        {"name": "David Okafor", "role": "Full-stack Engineer","capacity": 5},
        {"name": "Eva Petrov",   "role": "QA Engineer",        "capacity": 4},
    ]

    scheduled = get_store().query_tasks(status=TaskStatus.SCHEDULED.value)
    in_progress = get_store().query_tasks(status=TaskStatus.IN_PROGRESS.value)
    active = scheduled + in_progress

    for member in team:
        load = sum(1 for t in active if t.assignee == member["name"])
        member["current_load"] = load
        member["available_slots"] = member["capacity"] - load

    return json.dumps(team, indent=2)


def get_open_sprint() -> str:
    today = datetime.utcnow()
    sprint_start = today - timedelta(days=today.weekday())
    sprint_end = sprint_start + timedelta(days=13)
    in_sprint = get_store().query_tasks(status=TaskStatus.IN_PROGRESS.value)
    return json.dumps(
        {
            "sprint_number": 12,
            "start": sprint_start.date().isoformat(),
            "end": sprint_end.date().isoformat(),
            "active_tasks": len(in_sprint),
            "capacity": 25,
        },
        indent=2,
    )


def check_overdue_tasks() -> str:
    now = datetime.utcnow().isoformat()
    active_statuses = [
        TaskStatus.TRIAGED.value,
        TaskStatus.SCHEDULED.value,
        TaskStatus.IN_PROGRESS.value,
        TaskStatus.BLOCKED.value,
    ]
    overdue = []
    for status in active_statuses:
        for t in get_store().query_tasks(status=status):
            if t.deadline and t.deadline.isoformat() < now:
                overdue.append(t.model_dump(mode="json"))
    return json.dumps(overdue, indent=2)


def check_blocked_tasks() -> str:
    tasks = get_store().query_tasks(status=TaskStatus.BLOCKED.value)
    return json.dumps([t.model_dump(mode="json") for t in tasks], indent=2)


def get_unassigned_p0s() -> str:
    tasks = get_store().query_tasks(priority="P0")
    unassigned = [t for t in tasks if not t.assignee]
    return json.dumps([t.model_dump(mode="json") for t in unassigned], indent=2)


def compute_velocity() -> str:
    completed = get_store().query_tasks(status=TaskStatus.COMPLETED.value)
    by_assignee: dict[str, int] = {}
    for t in completed:
        key = t.assignee or "unassigned"
        by_assignee[key] = by_assignee.get(key, 0) + 1
    return json.dumps(
        {
            "total_completed": len(completed),
            "by_assignee": by_assignee,
            "sprint_velocity": len(completed),
        },
        indent=2,
    )
