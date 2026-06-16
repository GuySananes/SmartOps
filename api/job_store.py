from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from api.schemas import AgentJobResponse, AgentJobStatus


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, AgentJobResponse] = {}
        self._lock = asyncio.Lock()

    async def create(self, agent: str) -> AgentJobResponse:
        job = AgentJobResponse(
            job_id=str(uuid.uuid4())[:8],
            agent=agent,
            status=AgentJobStatus.PENDING,
            created_at=datetime.utcnow(),
        )
        async with self._lock:
            self._jobs[job.job_id] = job
        return job

    async def get(self, job_id: str) -> Optional[AgentJobResponse]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def update(self, job_id: str, **kwargs: object) -> None:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job:
                self._jobs[job_id] = job.model_copy(update=kwargs)

    def all(self) -> list[AgentJobResponse]:
        return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)


_job_store: Optional[JobStore] = None


def get_job_store() -> JobStore:
    global _job_store
    if _job_store is None:
        _job_store = JobStore()
    return _job_store
