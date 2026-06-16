from __future__ import annotations

import pytest

from core.models import Priority, Task, TaskStatus
from core.task_store import TaskStore


@pytest.fixture(autouse=True)
def temp_db(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> TaskStore:
    """Replace the global task store with a fresh in-memory-like temp DB for each test."""
    import core.task_store as ts_module

    db_path = str(tmp_path / "test.db")  # type: ignore[operator]
    store = TaskStore(db_path)
    monkeypatch.setattr(ts_module, "_store", store)
    return store


@pytest.fixture
def sample_pending_task(temp_db: TaskStore) -> Task:
    task = Task(
        id="test001",
        title="Fix login bug",
        description="Users cannot log in on mobile Safari",
        status=TaskStatus.PENDING_TRIAGE,
    )
    temp_db.create_task(task)
    return task


@pytest.fixture
def sample_triaged_task(temp_db: TaskStore) -> Task:
    task = Task(
        id="test002",
        title="Add CSV export",
        description="Export analytics data to CSV",
        priority=Priority.P2,
        status=TaskStatus.TRIAGED,
        category="feature",
        tags=["analytics", "export"],
        estimated_effort="4h",
    )
    temp_db.create_task(task)
    return task
