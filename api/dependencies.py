from __future__ import annotations

from api.job_store import JobStore
from api.job_store import get_job_store as _get_job_store
from core.task_store import TaskStore
from core.task_store import get_store as _get_store


def get_task_store() -> TaskStore:
    return _get_store()


def get_job_store() -> JobStore:
    return _get_job_store()
