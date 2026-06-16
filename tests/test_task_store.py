from __future__ import annotations

from core.models import Escalation, Priority, Task, TaskStatus
from core.task_store import TaskStore


def test_create_and_get_task(temp_db: TaskStore) -> None:
    task = Task(title="Test task", description="A test task")
    temp_db.create_task(task)
    retrieved = temp_db.get_task(task.id)
    assert retrieved is not None
    assert retrieved.title == "Test task"
    assert retrieved.status == TaskStatus.PENDING_TRIAGE


def test_get_nonexistent_task(temp_db: TaskStore) -> None:
    assert temp_db.get_task("does-not-exist") is None


def test_update_task_status(temp_db: TaskStore, sample_pending_task: Task) -> None:
    updated = temp_db.update_task(sample_pending_task.id, status="triaged")
    assert updated is not None
    assert updated.status == TaskStatus.TRIAGED


def test_update_task_assignee(temp_db: TaskStore, sample_triaged_task: Task) -> None:
    updated = temp_db.update_task(
        sample_triaged_task.id, assignee="Alice Chen", status="scheduled"
    )
    assert updated is not None
    assert updated.assignee == "Alice Chen"
    assert updated.status == TaskStatus.SCHEDULED


def test_query_tasks_by_status(temp_db: TaskStore) -> None:
    for i in range(3):
        temp_db.create_task(
            Task(
                title=f"Pending {i}",
                description="...",
                status=TaskStatus.PENDING_TRIAGE,
            )
        )
    for i in range(2):
        temp_db.create_task(
            Task(title=f"Done {i}", description="...", status=TaskStatus.COMPLETED)
        )

    pending = temp_db.query_tasks(status="pending_triage")
    completed = temp_db.query_tasks(status="completed")
    assert len(pending) == 3
    assert len(completed) == 2


def test_query_tasks_by_priority(temp_db: TaskStore) -> None:
    temp_db.create_task(
        Task(
            title="Critical",
            description="...",
            priority=Priority.P0,
            status=TaskStatus.TRIAGED,
        )
    )
    temp_db.create_task(
        Task(
            title="Low",
            description="...",
            priority=Priority.P3,
            status=TaskStatus.TRIAGED,
        )
    )

    p0_tasks = temp_db.query_tasks(priority="P0")
    assert len(p0_tasks) == 1
    assert p0_tasks[0].title == "Critical"


def test_task_tags_roundtrip(temp_db: TaskStore) -> None:
    task = Task(title="Tagged", description="...", tags=["auth", "mobile", "bug"])
    temp_db.create_task(task)
    retrieved = temp_db.get_task(task.id)
    assert retrieved is not None
    assert retrieved.tags == ["auth", "mobile", "bug"]


def test_create_and_get_escalation(
    temp_db: TaskStore, sample_pending_task: Task
) -> None:
    escalation = Escalation(task_id=sample_pending_task.id, reason="Overdue by 3 days")
    temp_db.create_escalation(escalation)
    escalations = temp_db.get_escalations(task_id=sample_pending_task.id)
    assert len(escalations) == 1
    assert escalations[0].reason == "Overdue by 3 days"
    assert not escalations[0].notified
