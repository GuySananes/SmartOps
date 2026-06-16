from __future__ import annotations

import json
from collections import Counter

from fastapi import APIRouter, Depends

from api.dependencies import get_task_store
from api.schemas import (
    SprintResponse,
    SystemStatusResponse,
    TaskResponse,
    TeamCapacityResponse,
    TeamMemberCapacity,
    VelocityResponse,
)
from core.agent_registry import AGENT_REGISTRY
from core.task_store import TaskStore
from tools.search_tools import (
    check_blocked_tasks,
    check_overdue_tasks,
    compute_velocity,
    get_open_sprint,
    get_team_capacity,
    get_unassigned_p0s,
)

router = APIRouter()


@router.get("/status", response_model=SystemStatusResponse)
def get_status(store: TaskStore = Depends(get_task_store)) -> SystemStatusResponse:
    from core import config

    tasks = store.query_tasks()
    counts = dict(Counter(t.status.value for t in tasks))
    return SystemStatusResponse(
        status="ok",
        agent_count=len(AGENT_REGISTRY),
        agents=list(AGENT_REGISTRY.keys()),
        task_counts=counts,
        db_path=config.DATABASE_PATH,
    )


@router.get("/capacity", response_model=TeamCapacityResponse)
def get_capacity() -> TeamCapacityResponse:
    data: list[dict] = json.loads(get_team_capacity())
    members = [TeamMemberCapacity(**m) for m in data]
    return TeamCapacityResponse(
        members=members,
        total_capacity=sum(m.capacity for m in members),
        total_load=sum(m.current_load for m in members),
        total_available=sum(m.available_slots for m in members),
    )


@router.get("/sprint", response_model=SprintResponse)
def get_sprint() -> SprintResponse:
    data: dict = json.loads(get_open_sprint())
    return SprintResponse(**data)


@router.get("/velocity", response_model=VelocityResponse)
def get_velocity() -> VelocityResponse:
    data: dict = json.loads(compute_velocity())
    return VelocityResponse(**data)


@router.get("/overdue", response_model=list[TaskResponse])
def get_overdue(store: TaskStore = Depends(get_task_store)) -> list[TaskResponse]:
    from core.models import Task

    data: list[dict] = json.loads(check_overdue_tasks())
    return [TaskResponse.model_validate(Task(**t)) for t in data]


@router.get("/blocked", response_model=list[TaskResponse])
def get_blocked(store: TaskStore = Depends(get_task_store)) -> list[TaskResponse]:
    from core.models import Task

    data: list[dict] = json.loads(check_blocked_tasks())
    return [TaskResponse.model_validate(Task(**t)) for t in data]


@router.get("/unassigned-p0s", response_model=list[TaskResponse])
def get_unassigned_p0s_route(store: TaskStore = Depends(get_task_store)) -> list[TaskResponse]:
    from core.models import Task

    data: list[dict] = json.loads(get_unassigned_p0s())
    return [TaskResponse.model_validate(Task(**t)) for t in data]
